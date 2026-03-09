"""Clone stamp technique — mirrors pixels from adjacent area over the watermark.

Clones from the direction recommended by the AI analysis (above, below, left, right).
Applies vertical/horizontal flip and gradient blending for seamless results.
"""

from __future__ import annotations

import numpy as np
from PIL import Image, ImageFilter

from unwatermark.core.techniques.base import RemovalTechnique
from unwatermark.models.analysis import WatermarkAnalysis, WatermarkRegion


class CloneStampTechnique(RemovalTechnique):

    @property
    def name(self) -> str:
        return "Clone Stamp"

    def remove(
        self,
        image: Image.Image,
        region: WatermarkRegion,
        analysis: WatermarkAnalysis,
    ) -> Image.Image:
        result = image.copy().convert("RGBA")
        direction = analysis.clone_direction

        source_strip = self._get_source_strip(result, region, direction)
        if source_strip is None:
            return self._fallback_blur(result, region)

        # Resize to match watermark region if needed
        if source_strip.size != (region.width, region.height):
            source_strip = source_strip.resize(
                (region.width, region.height), Image.LANCZOS
            )

        mask = self._build_gradient_mask(region.width, region.height, margin=20)
        result.paste(source_strip, (region.x, region.y), mask)
        return result

    def _get_source_strip(
        self,
        image: Image.Image,
        region: WatermarkRegion,
        direction: str,
    ) -> Image.Image | None:
        """Clone pixels from the specified direction, flipped to align edges."""
        img_w, img_h = image.size

        if direction == "above":
            source_y = max(0, region.y - region.height)
            source_h = region.y - source_y
            if source_h < 10:
                return None
            strip = image.crop((region.x, source_y, region.x2, source_y + source_h))
            return strip.transpose(Image.FLIP_TOP_BOTTOM)

        elif direction == "below":
            source_y = region.y2
            source_h = min(region.height, img_h - region.y2)
            if source_h < 10:
                return None
            strip = image.crop((region.x, source_y, region.x2, source_y + source_h))
            return strip.transpose(Image.FLIP_TOP_BOTTOM)

        elif direction == "left":
            source_x = max(0, region.x - region.width)
            source_w = region.x - source_x
            if source_w < 10:
                return None
            strip = image.crop((source_x, region.y, source_x + source_w, region.y2))
            return strip.transpose(Image.FLIP_LEFT_RIGHT)

        elif direction == "right":
            source_x = region.x2
            source_w = min(region.width, img_w - region.x2)
            if source_w < 10:
                return None
            strip = image.crop((source_x, region.y, source_x + source_w, region.y2))
            return strip.transpose(Image.FLIP_LEFT_RIGHT)

        # Fallback: try above, then below
        for fallback_dir in ("above", "below", "left", "right"):
            if fallback_dir != direction:
                result = self._get_source_strip(image, region, fallback_dir)
                if result is not None:
                    return result
        return None

    def _build_gradient_mask(self, width: int, height: int, margin: int) -> Image.Image:
        margin = min(margin, width // 4, height // 4)
        mask = np.ones((height, width), dtype=np.float32)

        for i in range(margin):
            alpha = i / margin
            mask[i, :] *= alpha
            mask[height - 1 - i, :] *= alpha
            mask[:, i] *= alpha
            mask[:, width - 1 - i] *= alpha

        return Image.fromarray((mask * 255).astype(np.uint8), mode="L")

    def _fallback_blur(self, image: Image.Image, region: WatermarkRegion) -> Image.Image:
        """Last resort — gaussian blur the watermark region."""
        crop = image.crop((region.x, region.y, region.x2, region.y2))
        blurred = crop.filter(ImageFilter.GaussianBlur(radius=15))
        image.paste(blurred, (region.x, region.y))
        return image
