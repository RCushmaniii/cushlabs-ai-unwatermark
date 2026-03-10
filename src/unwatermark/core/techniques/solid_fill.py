"""Solid fill technique — samples border pixels and fills the watermark region.

Best for watermarks on solid-color or simple gradient backgrounds.
"""

from __future__ import annotations

import numpy as np
from PIL import Image

from unwatermark.core.techniques.base import RemovalTechnique
from unwatermark.models.analysis import BackgroundType, WatermarkAnalysis, WatermarkRegion


class SolidFillTechnique(RemovalTechnique):

    @property
    def name(self) -> str:
        return "Solid Fill"

    def remove(
        self,
        image: Image.Image,
        region: WatermarkRegion,
        analysis: WatermarkAnalysis,
    ) -> Image.Image:
        result = image.copy().convert("RGBA")

        if analysis.background_type == BackgroundType.GRADIENT:
            return self._gradient_fill(result, region)

        color = self._sample_border_color(result, region)
        return self._solid_fill(result, region, color)

    def _sample_border_color(
        self, image: Image.Image, region: WatermarkRegion
    ) -> tuple[int, ...]:
        """Sample pixels from just outside the watermark border to find the fill color."""
        arr = np.array(image)
        samples = []
        pad = 5

        # Sample strip above the watermark
        if region.y > pad:
            strip = arr[region.y - pad : region.y, region.x : region.x2]
            samples.append(strip.reshape(-1, strip.shape[-1]))

        # Sample strip below
        if region.y2 + pad < image.height:
            strip = arr[region.y2 : region.y2 + pad, region.x : region.x2]
            samples.append(strip.reshape(-1, strip.shape[-1]))

        # Sample strip left
        if region.x > pad:
            strip = arr[region.y : region.y2, region.x - pad : region.x]
            samples.append(strip.reshape(-1, strip.shape[-1]))

        # Sample strip right
        if region.x2 + pad < image.width:
            strip = arr[region.y : region.y2, region.x2 : region.x2 + pad]
            samples.append(strip.reshape(-1, strip.shape[-1]))

        if not samples:
            return (0, 0, 0, 255)

        all_samples = np.concatenate(samples, axis=0)
        median = np.median(all_samples, axis=0).astype(np.uint8)
        return tuple(median.tolist())

    def _solid_fill(
        self,
        image: Image.Image,
        region: WatermarkRegion,
        color: tuple[int, ...],
    ) -> Image.Image:
        """Fill the watermark region with a solid color and soft-edge blend."""
        fill = Image.new("RGBA", (region.width, region.height), color)
        mask = self._soft_edge_mask(region.width, region.height, margin=8)
        image.paste(fill, (region.x, region.y), mask)
        return image

    def _gradient_fill(self, image: Image.Image, region: WatermarkRegion) -> Image.Image:
        """Fill with an interpolated gradient sampled from the region borders."""
        arr = np.array(image, dtype=np.float32)
        pad = 5
        channels = arr.shape[2]

        def _safe_mean(sliced: np.ndarray, fallback: np.ndarray | None = None) -> np.ndarray:
            """Mean of a slice, with fallback if the slice is empty."""
            if sliced.size == 0:
                return fallback if fallback is not None else np.zeros(channels, dtype=np.float32)
            return sliced.reshape(-1, channels).mean(axis=0)

        # Sample colors at four edges
        top_slice = arr[max(0, region.y - pad) : region.y, region.x : region.x2]
        bottom_slice = arr[region.y2 : min(image.height, region.y2 + pad), region.x : region.x2]
        left_slice = arr[region.y : region.y2, max(0, region.x - pad) : region.x]
        right_slice = arr[region.y : region.y2, region.x2 : min(image.width, region.x2 + pad)]

        top = _safe_mean(top_slice)
        bottom = _safe_mean(bottom_slice, top)
        left = _safe_mean(left_slice, top)
        right = _safe_mean(right_slice, bottom)

        # Bilinear interpolation: blend four corners properly
        h, w = region.height, region.width
        if h < 1 or w < 1:
            return image

        ys = np.linspace(0, 1, h)[:, None, None]
        xs = np.linspace(0, 1, w)[None, :, None]

        # Four-corner bilinear: top-left, top-right, bottom-left, bottom-right
        tl = (top + left) / 2.0
        tr = (top + right) / 2.0
        bl = (bottom + left) / 2.0
        br = (bottom + right) / 2.0

        top_row = tl * (1 - xs) + tr * xs
        bottom_row = bl * (1 - xs) + br * xs
        blended = top_row * (1 - ys) + bottom_row * ys

        patch = np.clip(blended, 0, 255).astype(np.uint8)
        fill = Image.fromarray(patch, mode=image.mode)

        mask = self._soft_edge_mask(w, h, margin=12)
        image.paste(fill, (region.x, region.y), mask)
        return image

    def _soft_edge_mask(self, width: int, height: int, margin: int) -> Image.Image:
        """Gradient mask that fades at edges for seamless blending."""
        margin = min(margin, width // 4, height // 4, 20)
        mask = np.ones((height, width), dtype=np.float32)

        for i in range(margin):
            alpha = i / margin
            mask[i, :] *= alpha
            mask[height - 1 - i, :] *= alpha
            mask[:, i] *= alpha
            mask[:, width - 1 - i] *= alpha

        return Image.fromarray((mask * 255).astype(np.uint8), mode="L")
