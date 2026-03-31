"""Lang-SAM watermark detection & mask refinement via Replicate.

Two modes:
1. **Standalone detection** — text-prompted segmentation finds watermarks,
   produces pixel-perfect masks. One API call: detection + masking (~$0.0014).
2. **Mask refinement** — Takes an existing bounding box (from Claude Vision or OCR)
   and generates a pixel-perfect mask for just that region. Precise masks instead
   of rectangles = no collateral damage to content.

Both modes return binary masks (white=watermark, black=keep) that feed directly
into LaMa inpainting via WatermarkAnalysis.mask.

Uses tmappdev/lang-segment-anything (GroundingDINO + SAM wrapper).
"""

from __future__ import annotations

import io
import logging

import numpy as np
from PIL import Image

from unwatermark.models.analysis import (
    BackgroundType,
    RemovalStrategy,
    WatermarkAnalysis,
    WatermarkRegion,
)

logger = logging.getLogger(__name__)

# Lang-SAM model on Replicate (GroundingDINO + SAM, text-prompted segmentation)
_LANG_SAM_MODEL = (
    "tmappdev/lang-segment-anything:"
    "891411c38a6ed2d44c004b7b9e44217df7a5b07848f29ddefd2e28bc7cbf93bc"
)


def detect_watermark_sam(
    image: Image.Image,
    replicate_api_token: str | None = None,
    detection_prompt: str | None = None,
    max_mask_percent: float = 10.0,
) -> WatermarkAnalysis | None:
    """Detect watermarks using Grounded SAM on Replicate.

    Args:
        image: PIL Image to analyze.
        replicate_api_token: Replicate API token.
        detection_prompt: Custom prompt for Grounding DINO (e.g. "NotebookLM logo").
        max_mask_percent: Max percentage of image area a valid watermark mask can cover.

    Returns:
        WatermarkAnalysis with pixel-perfect mask, or None if no watermark found.
    """
    if not replicate_api_token:
        logger.warning("No Replicate API token — skipping SAM detection")
        return None

    try:
        from unwatermark.config import get_replicate_client
        client = get_replicate_client(replicate_api_token)
    except (ImportError, RuntimeError):
        logger.warning("Replicate package not installed — skipping SAM detection")
        return None

    # Build the mask prompt
    if detection_prompt:
        mask_prompt = detection_prompt
    else:
        mask_prompt = "watermark"

    # Encode image — JPEG for smaller payload (detection doesn't need lossless)
    img_bytes = io.BytesIO()
    image.convert("RGB").save(img_bytes, format="JPEG", quality=85)
    img_bytes.seek(0)

    try:
        logger.info(f"Lang-SAM: detecting '{mask_prompt}'...")
        output = client.run(
            _LANG_SAM_MODEL,
            input={
                "image": img_bytes,
                "text_prompt": mask_prompt,
            },
        )

        # Lang-SAM returns a single mask image (FileOutput or URL string)
        mask_image = _fetch_mask_output(output)
        if mask_image is None:
            logger.info("Lang-SAM: no mask output returned")
            return None

    except Exception as e:
        logger.warning(f"Lang-SAM detection failed: {e}")
        return None

    # Analyze the mask to check if anything was found
    mask_arr = np.array(mask_image)
    white_pixels = np.sum(mask_arr > 128)
    total_pixels = mask_arr.size

    if white_pixels == 0:
        logger.info("Lang-SAM: mask is empty — no watermark found")
        return None

    mask_percent = (white_pixels / total_pixels) * 100
    logger.info(f"Lang-SAM: mask covers {mask_percent:.1f}% of image")

    if mask_percent > max_mask_percent:
        logger.warning(
            f"Lang-SAM: mask too large ({mask_percent:.1f}% > {max_mask_percent}%) — "
            "likely false positive, skipping"
        )
        return None

    # Derive bounding box from the mask
    rows = np.any(mask_arr > 128, axis=1)
    cols = np.any(mask_arr > 128, axis=0)
    y_min, y_max = np.where(rows)[0][[0, -1]]
    x_min, x_max = np.where(cols)[0][[0, -1]]

    region = WatermarkRegion(
        x=int(x_min),
        y=int(y_min),
        width=int(x_max - x_min + 1),
        height=int(y_max - y_min + 1),
    )

    # Resize mask to match input image if needed
    if mask_image.size != image.size:
        mask_image = mask_image.resize(image.size, Image.NEAREST)

    logger.info(
        f"Lang-SAM: found watermark at ({region.x},{region.y},{region.width}x{region.height})"
    )

    return WatermarkAnalysis(
        watermark_found=True,
        region=region,
        description=f"Lang-SAM: '{mask_prompt}'",
        background_type=BackgroundType.MIXED,
        strategy=RemovalStrategy.INPAINT,
        confidence=0.9,
        reasoning="Lang-SAM pixel-perfect segmentation with LaMa inpainting",
        mask=mask_image,
    )


def refine_with_sam(
    image: Image.Image,
    analysis: WatermarkAnalysis,
    replicate_api_token: str | None = None,
    max_mask_percent: float = 10.0,
) -> Image.Image | None:
    """Refine an existing detection with a pixel-perfect SAM mask.

    Takes a WatermarkAnalysis (from Florence-2 or OCR) that has a bounding box
    but no pixel mask, and calls Grounded SAM to generate a precise mask within
    that region. The mask covers only the actual watermark pixels, not the
    surrounding content — this is what prevents LaMa from damaging nearby text.

    Args:
        image: Full PIL Image.
        analysis: Existing detection with bounding box (from Florence-2/OCR).
        replicate_api_token: Replicate API token.
        max_mask_percent: Max percentage of image area the mask can cover.

    Returns:
        PIL Image mask (L mode, white=watermark) or None if refinement fails.
    """
    if not replicate_api_token:
        return None

    try:
        from unwatermark.config import get_replicate_client
        client = get_replicate_client(replicate_api_token)
    except (ImportError, RuntimeError):
        logger.warning("Replicate package not installed — skipping SAM refinement")
        return None

    mask_prompt = "watermark text"

    # Crop to the detection region with a capped margin — large enough for SAM
    # to see context around the watermark, but small enough to avoid pulling in
    # distant content text (which SAM would segment as "watermark text").
    r = analysis.region
    # 50% of region size, but never more than 3% of image dimension
    max_margin = int(max(image.width, image.height) * 0.03)
    margin = min(max(r.width, r.height) // 2, max_margin)
    crop_x1 = max(0, r.x - margin)
    crop_y1 = max(0, r.y - margin)
    crop_x2 = min(image.width, r.x + r.width + margin)
    crop_y2 = min(image.height, r.y + r.height + margin)
    crop = image.crop((crop_x1, crop_y1, crop_x2, crop_y2))

    logger.info(
        f"SAM refinement: cropped to ({crop_x1},{crop_y1})-({crop_x2},{crop_y2}) "
        f"({crop.width}x{crop.height}) around detection region"
    )

    img_bytes = io.BytesIO()
    crop.convert("RGB").save(img_bytes, format="JPEG", quality=85)
    img_bytes.seek(0)

    try:
        logger.info(f"SAM refinement: generating pixel mask for '{mask_prompt}'...")
        output = client.run(
            _LANG_SAM_MODEL,
            input={
                "image": img_bytes,
                "text_prompt": mask_prompt,
            },
        )

        crop_mask = _fetch_mask_output(output)
        if crop_mask is None:
            logger.info("SAM refinement: no mask output")
            return None

    except Exception as e:
        logger.warning(f"SAM refinement failed: {e}")
        return None

    # Resize crop mask to match crop dimensions if needed
    if crop_mask.size != crop.size:
        crop_mask = crop_mask.resize(crop.size, Image.NEAREST)

    # Validate the crop mask
    crop_arr = np.array(crop_mask)
    white_pixels = np.sum(crop_arr > 128)

    if white_pixels == 0:
        logger.info("SAM refinement: empty mask — SAM couldn't find the watermark")
        return None

    crop_mask_percent = (white_pixels / crop_arr.size) * 100
    # Allow up to 50% of the crop region (which is already small and focused)
    if crop_mask_percent > 50.0:
        logger.warning(
            f"SAM refinement: crop mask too large ({crop_mask_percent:.1f}%) — rejecting"
        )
        return None

    # Map cropped mask back to full-image coordinates
    full_mask = Image.new("L", image.size, 0)
    full_mask.paste(crop_mask, (crop_x1, crop_y1))

    full_arr = np.array(full_mask)
    full_percent = (np.sum(full_arr > 128) / full_arr.size) * 100
    logger.info(f"SAM refinement: pixel-perfect mask covers {full_percent:.1f}% of image")

    return full_mask


def _fetch_mask_output(output) -> Image.Image | None:
    """Fetch the mask image from Lang-SAM's Replicate output.

    Lang-SAM returns a single mask image (FileOutput, URL string, or iterator).
    Handles all Replicate SDK output variations.
    """
    import urllib.request

    # FileOutput object with .read()
    if hasattr(output, "read"):
        return Image.open(io.BytesIO(output.read())).convert("L")

    # URL string
    if isinstance(output, str):
        with urllib.request.urlopen(output) as resp:
            return Image.open(io.BytesIO(resp.read())).convert("L")

    # FileOutput with .url attribute
    if hasattr(output, "url"):
        with urllib.request.urlopen(str(output.url)) as resp:
            return Image.open(io.BytesIO(resp.read())).convert("L")

    # Iterator (e.g., list of outputs) — take the first one
    try:
        for item in output:
            if hasattr(item, "read"):
                return Image.open(io.BytesIO(item.read())).convert("L")
            url = str(item.url) if hasattr(item, "url") else str(item)
            with urllib.request.urlopen(url) as resp:
                return Image.open(io.BytesIO(resp.read())).convert("L")
    except (TypeError, StopIteration):
        pass

    return None
