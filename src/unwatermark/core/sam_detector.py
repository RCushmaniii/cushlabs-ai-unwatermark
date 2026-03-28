"""Grounded SAM watermark detection & mask refinement via Replicate.

Two modes:
1. **Standalone detection** — Grounding DINO finds watermarks by text prompt,
   SAM creates pixel-perfect masks. One API call: detection + masking (~$0.003).
2. **Mask refinement** — Takes an existing bounding box (from Florence-2 or OCR)
   and generates a pixel-perfect SAM mask for just that region. This is the v2
   upgrade: precise masks instead of rectangles = no collateral damage to content.

Both modes return binary masks (white=watermark, black=keep) that feed directly
into LaMa inpainting via WatermarkAnalysis.mask.
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

# Grounded SAM model on Replicate (version hash required)
_GROUNDED_SAM_MODEL = (
    "schananas/grounded_sam:"
    "ee871c19efb1941f55f66a3d7d960428c8a5afcb77449547fe8e5a3ab9ebc21c"
)

# Default prompts to detect watermarks
_DEFAULT_PROMPTS = [
    "watermark",
    "watermark text overlay",
]


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
        logger.info(f"Grounded SAM: detecting '{mask_prompt}'...")
        output = client.run(
            _GROUNDED_SAM_MODEL,
            input={
                "image": img_bytes,
                "mask_prompt": mask_prompt,
                "adjustment_factor": 0,
            },
        )

        # Output is a list of 4 image URLs:
        # [0] annotated positive mask, [1] annotated negative mask,
        # [2] binary mask, [3] inverted mask
        output_list = list(output)
        if len(output_list) < 3:
            logger.info("Grounded SAM: no output returned")
            return None

        # Get the binary mask (index 2)
        mask_url = output_list[2]
        if hasattr(mask_url, "url"):
            mask_url = mask_url.url
        mask_url = str(mask_url)

        import urllib.request
        with urllib.request.urlopen(mask_url) as resp:
            mask_image = Image.open(io.BytesIO(resp.read())).convert("L")

    except Exception as e:
        logger.warning(f"Grounded SAM detection failed: {e}")
        return None

    # Analyze the mask to check if anything was found
    mask_arr = np.array(mask_image)
    white_pixels = np.sum(mask_arr > 128)
    total_pixels = mask_arr.size

    if white_pixels == 0:
        logger.info("Grounded SAM: mask is empty — no watermark found")
        return None

    mask_percent = (white_pixels / total_pixels) * 100
    logger.info(f"Grounded SAM: mask covers {mask_percent:.1f}% of image")

    if mask_percent > max_mask_percent:
        logger.warning(
            f"Grounded SAM: mask too large ({mask_percent:.1f}% > {max_mask_percent}%) — "
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

    # Resize mask to match input image if needed (Grounded SAM may resize)
    if mask_image.size != image.size:
        mask_image = mask_image.resize(image.size, Image.NEAREST)

    logger.info(
        f"Grounded SAM: found watermark at ({region.x},{region.y},{region.width}x{region.height})"
    )

    return WatermarkAnalysis(
        watermark_found=True,
        region=region,
        description=f"Grounded SAM: '{mask_prompt}'",
        background_type=BackgroundType.MIXED,
        strategy=RemovalStrategy.INPAINT,
        confidence=0.9,
        reasoning="Grounded SAM pixel-perfect segmentation with LaMa inpainting",
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

    # Build a focused prompt from the detection description
    desc = (analysis.description or "").lower()
    if "notebooklm" in desc:
        mask_prompt = "NotebookLM watermark logo text"
    elif "shutterstock" in desc:
        mask_prompt = "Shutterstock watermark text"
    elif any(kw in desc for kw in ["florence", "ocr", "text watermark"]):
        # Extract the actual watermark text from descriptions like
        # "Florence-2 OCR: 'NotebookLM'" or "Text watermark: 'SAMPLE'"
        import re
        text_match = re.search(r"'([^']+)'", analysis.description)
        if text_match:
            mask_prompt = f"{text_match.group(1)} watermark"
        else:
            mask_prompt = "watermark text overlay"
    else:
        mask_prompt = "watermark"

    # Encode the full image — JPEG for smaller payload, SAM doesn't need lossless
    img_bytes = io.BytesIO()
    image.convert("RGB").save(img_bytes, format="JPEG", quality=85)
    img_bytes.seek(0)

    try:
        logger.info(f"SAM refinement: generating pixel mask for '{mask_prompt}'...")
        output = client.run(
            _GROUNDED_SAM_MODEL,
            input={
                "image": img_bytes,
                "mask_prompt": mask_prompt,
                "adjustment_factor": 0,
            },
        )

        output_list = list(output)
        if len(output_list) < 3:
            logger.info("SAM refinement: no mask output")
            return None

        # Get the binary mask (index 2)
        mask_url = output_list[2]
        if hasattr(mask_url, "url"):
            mask_url = mask_url.url
        mask_url = str(mask_url)

        import urllib.request
        with urllib.request.urlopen(mask_url) as resp:
            mask_image = Image.open(io.BytesIO(resp.read())).convert("L")

    except Exception as e:
        logger.warning(f"SAM refinement failed: {e}")
        return None

    # Validate the mask
    mask_arr = np.array(mask_image)
    white_pixels = np.sum(mask_arr > 128)
    total_pixels = mask_arr.size

    if white_pixels == 0:
        logger.info("SAM refinement: empty mask — SAM couldn't find the watermark")
        return None

    mask_percent = (white_pixels / total_pixels) * 100
    if mask_percent > max_mask_percent:
        logger.warning(
            f"SAM refinement: mask too large ({mask_percent:.1f}%) — rejecting"
        )
        return None

    # Resize mask to match input image if needed
    if mask_image.size != image.size:
        mask_image = mask_image.resize(image.size, Image.NEAREST)

    logger.info(f"SAM refinement: pixel-perfect mask covers {mask_percent:.1f}% of image")
    return mask_image
