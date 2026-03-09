"""Watermark removal via clone-stamp with vertical flip and gradient blending.

The technique:
1. Take a source strip from just ABOVE the watermark region (same width, same height).
2. Vertically flip the source strip so the edge nearest the watermark blends naturally.
3. Create a gradient alpha mask that fades from full opacity at the watermark interior
   to transparent at the boundary, producing a seamless blend.
4. Composite the flipped source over the watermark region using the gradient mask.
"""

import numpy as np
from PIL import Image

from unwatermark.core.detector import WatermarkRegion


def remove_watermark(
    image: Image.Image,
    region: WatermarkRegion,
    blend_margin: int = 20,
) -> Image.Image:
    """Remove a watermark by cloning pixels from above the region.

    Args:
        image: Source PIL Image (will not be mutated).
        region: The watermark bounding box to remove.
        blend_margin: Pixels of gradient blending at the boundary.

    Returns:
        New PIL Image with the watermark region patched.
    """
    result = image.copy().convert("RGBA")
    img_w, img_h = result.size

    # Determine source region (directly above the watermark)
    source_y = max(0, region.y - region.height)
    source_height = region.y - source_y

    if source_height < 10:
        # Not enough room above — try below instead
        source_y = region.y2
        source_height = min(region.height, img_h - region.y2)

    if source_height < 10:
        # Fallback: just blur the region
        return _fallback_blur(result, region)

    # Crop the source strip
    source_strip = result.crop((region.x, source_y, region.x2, source_y + source_height))

    # Vertically flip so the edge closest to the watermark lines up naturally
    source_strip = source_strip.transpose(Image.FLIP_TOP_BOTTOM)

    # If source strip height differs from watermark region height, resize to match
    if source_strip.height != region.height:
        source_strip = source_strip.resize((region.width, region.height), Image.LANCZOS)

    # Build gradient alpha mask for smooth blending
    mask = _build_gradient_mask(region.width, region.height, blend_margin)

    # Composite: paste the cloned strip over the watermark area
    result.paste(source_strip, (region.x, region.y), mask)

    return result


def _build_gradient_mask(width: int, height: int, margin: int) -> Image.Image:
    """Create a gradient alpha mask that's full-opacity in the center and fades at edges.

    This prevents hard seams at the clone boundary.
    """
    margin = min(margin, width // 4, height // 4)
    mask = np.ones((height, width), dtype=np.float32)

    # Top edge fade
    for i in range(margin):
        alpha = i / margin
        mask[i, :] *= alpha

    # Bottom edge fade
    for i in range(margin):
        alpha = i / margin
        mask[height - 1 - i, :] *= alpha

    # Left edge fade
    for i in range(margin):
        alpha = i / margin
        mask[:, i] *= alpha

    # Right edge fade
    for i in range(margin):
        alpha = i / margin
        mask[:, width - 1 - i] *= alpha

    mask_uint8 = (mask * 255).astype(np.uint8)
    return Image.fromarray(mask_uint8, mode="L")


def _fallback_blur(image: Image.Image, region: WatermarkRegion) -> Image.Image:
    """Last-resort fallback: gaussian blur the watermark region."""
    from PIL import ImageFilter

    crop = image.crop((region.x, region.y, region.x2, region.y2))
    blurred = crop.filter(ImageFilter.GaussianBlur(radius=15))
    image.paste(blurred, (region.x, region.y))
    return image
