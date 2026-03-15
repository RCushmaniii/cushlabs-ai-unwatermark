"""Alpha subtraction technique — removes semi-transparent watermark overlays.

Instead of inpainting (erase and fill), this technique directly subtracts the
watermark contamination from each pixel. For each watermark pixel, we estimate
what the local background SHOULD look like (via median filter), compute the
deviation the watermark introduced, and subtract it.

    contamination = pixel - local_background
    cleaned = pixel - strength * contamination
           = pixel - strength * (pixel - local_background)

Works for both directions:
- White/light watermark on dark bg → pixel is brighter than background → subtract positive deviation
- Gray/dark watermark on light bg → pixel is darker than background → subtract negative deviation

The strength multiplier (>1.0) compensates for the median filter underestimating
the true background (because watermark pixels pull the median).

Preserves content perfectly because non-watermark pixels have zero deviation
from their local background, so nothing gets subtracted.
"""

from __future__ import annotations

import logging

import numpy as np
from PIL import Image

from unwatermark.core.techniques.base import RemovalTechnique
from unwatermark.models.analysis import WatermarkAnalysis, WatermarkRegion

logger = logging.getLogger(__name__)


class AlphaSubtractTechnique(RemovalTechnique):

    @property
    def name(self) -> str:
        return "Alpha Subtraction"

    def remove(
        self,
        image: Image.Image,
        region: WatermarkRegion,
        analysis: WatermarkAnalysis,
    ) -> Image.Image:
        # Run 2-3 internal passes — each pass re-estimates the background
        # from the (partially cleaned) image, catching residual watermark.
        # More than 3 passes degrades image quality (texture gets washed out).
        current = image
        for internal_pass in range(1, 4):
            result, wm_typical = self._single_pass(current, region, internal_pass)
            if result is None:
                break  # no watermark pixels detected
            current = result
            # Stop early if watermark is strong (1-2 passes enough)
            if internal_pass >= 2 and wm_typical > 10:
                break
        return current

    def _single_pass(
        self,
        image: Image.Image,
        region: WatermarkRegion,
        pass_num: int,
    ) -> tuple[Image.Image | None, float]:
        """Run one pass of alpha subtraction. Returns (result, wm_typical) or (None, 0)."""
        from scipy.ndimage import median_filter

        img_arr = np.array(image, dtype=np.float64)
        h, w = img_arr.shape[:2]

        # Work in grayscale for watermark detection
        gray = np.array(image.convert("L"), dtype=np.float64)

        # Local background estimate — median filter "ignores" watermark text
        # when kernel is larger than stroke width.
        # Larger kernel (51) on later passes for better background estimate
        # after partial watermark removal.
        kernel_size = 51 if pass_num > 1 else 31
        bg_gray = median_filter(gray, size=kernel_size)

        # Deviation from local background reveals watermark
        deviation = gray - bg_gray

        # Region bounds
        y1, y2 = max(0, region.y), min(h, region.y2)
        x1, x2 = max(0, region.x), min(w, region.x2)

        # Detect watermark direction within the region
        region_dev = deviation[y1:y2, x1:x2]
        pos_energy = np.sum(region_dev[region_dev > 3] ** 2)
        neg_energy = np.sum(region_dev[region_dev < -3] ** 2)

        if neg_energy > pos_energy:
            direction = "darker"
        else:
            direction = "lighter"

        if pass_num == 1:
            logger.debug(
                f"Watermark direction: {direction} "
                f"(pos_energy={pos_energy:.0f}, neg_energy={neg_energy:.0f})"
            )

        # Build watermark mask
        mask = self._build_mask(deviation, direction, y1, y2, x1, x2, h, w)

        if mask is None:
            if pass_num == 1:
                logger.info("Alpha subtraction: could not detect watermark pixels, skipping")
            return None, 0.0

        # Estimate per-channel local background for RGB subtraction
        bg_rgb = np.stack([
            median_filter(img_arr[:, :, c], size=kernel_size)
            for c in range(3)
        ], axis=-1)

        # Compute per-pixel RGB contamination
        contamination = img_arr - bg_rgb

        # Per-pixel adaptive correction weight
        abs_dev = np.abs(deviation)

        core_devs = abs_dev[mask > 0.5]
        if len(core_devs) > 10:
            wm_typical = float(np.percentile(core_devs, 25))
        else:
            wm_typical = 15.0

        # Transition zone: full correction below 2.5x typical, zero above 5x typical
        low = max(wm_typical * 2.5, 30.0)
        high = max(wm_typical * 5.0, 60.0)
        if high - low < 15:
            high = low + 15

        weight = np.clip((high - abs_dev) / (high - low), 0.0, 1.0)

        # Base strength: push harder on faint watermarks
        if wm_typical < 5:
            base_strength = 3.5
        elif wm_typical < 10:
            base_strength = 2.5
        elif wm_typical < 15:
            base_strength = 2.0
        else:
            base_strength = 1.5

        logger.info(
            f"Alpha subtraction pass {pass_num}: direction={direction}, "
            f"wm_typical={wm_typical:.1f}, base_strength={base_strength:.1f}, "
            f"masked_pixels={np.sum(mask > 0.01):.0f}"
        )

        # Cap per-channel correction
        max_per_channel = 50.0

        result = img_arr.copy()
        for c in range(3):
            correction = base_strength * weight * mask * contamination[:, :, c]
            correction = np.clip(correction, -max_per_channel, max_per_channel)
            result[:, :, c] -= correction

        return Image.fromarray(np.clip(result, 0, 255).astype(np.uint8)), wm_typical

    def _build_mask(
        self,
        deviation: np.ndarray,
        direction: str,
        y1: int, y2: int, x1: int, x2: int,
        h: int, w: int,
    ) -> np.ndarray | None:
        """Build a soft mask of watermark pixels."""
        from scipy.ndimage import (
            binary_closing, binary_dilation, binary_opening,
            distance_transform_edt,
        )

        # Region-only mask
        region_mask = np.zeros((h, w), dtype=bool)
        region_mask[y1:y2, x1:x2] = True

        # Adaptive threshold based on image noise floor.
        # The median absolute deviation of the non-watermark pixels estimates
        # the image's natural texture variation. We threshold at 2x the noise
        # floor to avoid correcting natural texture.
        region_dev_abs = np.abs(deviation[y1:y2, x1:x2])
        noise_floor = float(np.median(region_dev_abs))
        threshold = max(5.0, noise_floor * 2.0)
        logger.debug(
            f"Alpha subtraction: noise_floor={noise_floor:.1f}, threshold={threshold:.1f}"
        )

        if direction == "darker":
            wm_pixels = region_mask & (deviation < -threshold)
        else:
            wm_pixels = region_mask & (deviation > threshold)

        # Morphological cleanup
        struct = np.ones((3, 3))
        wm_pixels = binary_opening(wm_pixels, structure=struct, iterations=1)
        wm_pixels = binary_closing(wm_pixels, structure=struct, iterations=2)

        # Coverage check
        region_pixel_count = np.sum(region_mask)
        if region_pixel_count == 0:
            return None

        coverage = np.sum(wm_pixels) / region_pixel_count
        logger.debug(f"Alpha subtraction: watermark coverage = {coverage:.1%}")

        if coverage < 0.005 or coverage > 0.90:
            return None

        # Feather edges for smooth blending
        core = wm_pixels
        dilated = binary_dilation(core, structure=struct, iterations=3)

        # Build soft mask: 1.0 at core, fading at edges
        soft = np.zeros((h, w), dtype=np.float64)
        soft[core] = 1.0

        edge_zone = dilated & ~core
        if np.any(edge_zone):
            dist = distance_transform_edt(~core)
            max_dist = dist[edge_zone].max()
            if max_dist > 0:
                fade = 1.0 - np.clip(dist / (max_dist + 1), 0, 1)
                soft[edge_zone] = fade[edge_zone]

        return soft

