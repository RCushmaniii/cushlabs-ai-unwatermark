"""Grounded SAM watermark detection — text-prompted segmentation via Replicate.

Uses Grounding DINO to find watermarks by text prompt, then SAM to create
pixel-perfect masks. Returns both the bounding box (for analysis) and the
binary mask (for precise inpainting that doesn't damage surrounding content).

One API call does both detection AND masking at ~$0.003/run, ~4 seconds.
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
    max_mask_percent: float = 25.0,
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
    try:
        import replicate
    except ImportError:
        logger.warning("Replicate package not installed — skipping SAM detection")
        return None

    if not replicate_api_token:
        logger.warning("No Replicate API token — skipping SAM detection")
        return None

    client = replicate.Client(api_token=replicate_api_token)

    # Build the mask prompt
    if detection_prompt:
        mask_prompt = detection_prompt
    else:
        mask_prompt = "watermark"

    # Encode image
    img_bytes = io.BytesIO()
    image.convert("RGB").save(img_bytes, format="PNG")
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
