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
        pad = 3

        # Sample colors at four edges
        top = arr[max(0, region.y - pad) : region.y, region.x : region.x2].mean(axis=(0, 1))
        bottom = arr[region.y2 : min(image.height, region.y2 + pad), region.x : region.x2].mean(
            axis=(0, 1)
        )
        left = arr[region.y : region.y2, max(0, region.x - pad) : region.x].mean(axis=(0, 1))
        right = arr[region.y : region.y2, region.x2 : min(image.width, region.x2 + pad)].mean(
            axis=(0, 1)
        )

        # Bilinear interpolation across the region
        h, w = region.height, region.width
        ys = np.linspace(0, 1, h)[:, None, None]
        xs = np.linspace(0, 1, w)[None, :, None]

        # Interpolate vertically then horizontally
        vert = top * (1 - ys) + bottom * ys
        horiz = left * (1 - xs) + right * xs
        blended = (vert + horiz) / 2.0

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
