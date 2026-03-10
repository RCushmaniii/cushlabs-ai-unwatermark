"""Florence-2 watermark detection via Replicate API.

Uses Microsoft's Florence-2 vision foundation model for open-vocabulary
watermark detection. Unlike EasyOCR (text only) or Claude Vision (expensive,
non-deterministic), Florence-2 handles text, logos, and visual watermarks
at ~$0.001 per call with consistent results.

This is the v2 detection layer — replaces Claude Vision as the AI fallback
when EasyOCR finds no text watermarks.
"""

from __future__ import annotations

import io
import base64
import json
import logging

from PIL import Image

from unwatermark.models.analysis import (
    BackgroundType,
    RemovalStrategy,
    SurroundingContext,
    WatermarkAnalysis,
    WatermarkRegion,
)

logger = logging.getLogger(__name__)

# Default prompts that Florence-2 uses to find watermarks via open vocabulary detection.
# These are tried in order — first one that finds something wins.
_DETECTION_PROMPTS = [
    "watermark",
    "watermark text",
    "logo overlay",
    "text overlay",
]


def detect_watermark_florence(
    image: Image.Image,
    replicate_api_token: str | None = None,
    detection_prompt: str | None = None,
    max_bbox_percent: float = 15.0,
) -> WatermarkAnalysis | None:
    """Detect watermarks using Florence-2 via Replicate.

    Args:
        image: PIL Image to analyze.
        replicate_api_token: Replicate API token (uses env var if None).
        detection_prompt: Custom prompt for detection (e.g., "NotebookLM logo").
        max_bbox_percent: Maximum bounding box size as % of image area.
                          Boxes larger than this are filtered out (likely false positives).

    Returns:
        WatermarkAnalysis if watermark detected, None if nothing found.
    """
    import replicate

    if replicate_api_token:
        client = replicate.Client(api_token=replicate_api_token)
    else:
        client = replicate.Client()

    img_w, img_h = image.size
    img_area = img_w * img_h

    # Convert image to base64 data URI for Replicate
    img_uri = _image_to_data_uri(image)

    # Try detection prompts in order
    prompts_to_try = [detection_prompt] if detection_prompt else _DETECTION_PROMPTS

    for prompt in prompts_to_try:
        try:
            logger.info(f"Florence-2: trying prompt '{prompt}'")
            output = client.run(
                "lucataco/florence-2-large",
                input={
                    "image": img_uri,
                    "task": "<OPEN_VOCABULARY_DETECTION>",
                    "text_input": prompt,
                },
            )

            # Parse the response
            result = _parse_florence_output(output, img_w, img_h, img_area, max_bbox_percent)
            if result is not None:
                logger.info(
                    f"Florence-2: detected watermark with prompt '{prompt}' — "
                    f"region=({result.region.x},{result.region.y},"
                    f"{result.region.width}x{result.region.height})"
                )
                return result

        except Exception as e:
            logger.warning(f"Florence-2 detection failed with prompt '{prompt}': {e}")
            continue

    logger.info("Florence-2: no watermarks detected with any prompt")
    return None


def _image_to_data_uri(image: Image.Image) -> str:
    """Convert PIL Image to a base64 data URI for Replicate API."""
    buf = io.BytesIO()
    image.convert("RGB").save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{b64}"


def _parse_florence_output(
    output,
    img_w: int,
    img_h: int,
    img_area: int,
    max_bbox_percent: float,
) -> WatermarkAnalysis | None:
    """Parse Florence-2 open vocabulary detection output.

    Florence-2 returns results in various formats depending on the task.
    For OPEN_VOCABULARY_DETECTION, it returns bounding boxes and labels.
    """
    # Replicate output may be a string, dict, or iterator
    if isinstance(output, str):
        try:
            data = json.loads(output)
        except json.JSONDecodeError:
            logger.debug(f"Florence-2: could not parse output as JSON: {output[:200]}")
            return None
    elif isinstance(output, dict):
        data = output
    elif hasattr(output, '__iter__'):
        # Iterator — collect all parts
        parts = list(output)
        combined = "".join(str(p) for p in parts)
        try:
            data = json.loads(combined)
        except json.JSONDecodeError:
            logger.debug(f"Florence-2: could not parse iterator output: {combined[:200]}")
            return None
    else:
        logger.debug(f"Florence-2: unexpected output type: {type(output)}")
        return None

    # Extract bounding boxes — Florence-2 output format varies by task
    bboxes = []
    labels = []

    if isinstance(data, dict):
        # Try common Florence-2 output formats
        for key in data:
            val = data[key]
            if isinstance(val, dict):
                if "bboxes" in val:
                    bboxes = val["bboxes"]
                    labels = val.get("labels", [])
                elif "quad_boxes" in val:
                    # OCR_WITH_REGION format — convert quads to bboxes
                    for quad in val["quad_boxes"]:
                        xs = quad[0::2]
                        ys = quad[1::2]
                        bboxes.append([min(xs), min(ys), max(xs), max(ys)])
                    labels = val.get("labels", [])
            elif isinstance(val, list) and len(val) > 0:
                # Might be a list of bboxes directly
                if isinstance(val[0], (list, tuple)) and len(val[0]) == 4:
                    bboxes = val

    if not bboxes:
        # Try parsing as a results dict with 'results' key
        if "results" in data:
            for item in data["results"]:
                if "bbox" in item:
                    bboxes.append(item["bbox"])
                    labels.append(item.get("label", "watermark"))

    if not bboxes:
        return None

    # Filter by size — large boxes are likely false positives
    valid_boxes = []
    for i, bbox in enumerate(bboxes):
        x1, y1, x2, y2 = [int(v) for v in bbox[:4]]
        w = x2 - x1
        h = y2 - y1
        area = w * h
        pct = (area / img_area) * 100

        label = labels[i] if i < len(labels) else "watermark"

        if pct <= max_bbox_percent and w > 5 and h > 5:
            valid_boxes.append((x1, y1, w, h, pct, label))
            logger.debug(f"Florence-2: bbox ({x1},{y1},{w}x{h}) = {pct:.1f}% — accepted")
        else:
            logger.debug(f"Florence-2: bbox ({x1},{y1},{w}x{h}) = {pct:.1f}% — filtered out")

    if not valid_boxes:
        return None

    # Use the first valid detection (Florence-2 typically returns the most
    # confident detection first)
    x, y, w, h, pct, label = valid_boxes[0]

    # Add padding
    pad_x = max(5, int(img_w * 0.01))
    pad_y = max(5, int(img_h * 0.01))
    region = WatermarkRegion(x=x, y=y, width=w, height=h)
    padded = region.padded_xy(pad_x, pad_y, img_w, img_h)

    return WatermarkAnalysis(
        watermark_found=True,
        region=padded,
        description=f"Florence-2 detected: '{label}'",
        background_type=BackgroundType.MIXED,
        strategy=RemovalStrategy.INPAINT,
        confidence=0.85,
        reasoning=f"Florence-2 open vocabulary detection found '{label}' ({pct:.1f}% of image)",
        context=SurroundingContext(),
        clone_direction=_best_clone_direction(x, y, w, h, img_w, img_h),
    )


def _best_clone_direction(
    x: int, y: int, w: int, h: int, img_w: int, img_h: int
) -> str:
    """Determine the best direction to clone from based on watermark position."""
    cx = x + w / 2
    cy = y + h / 2
    distances = {
        "above": cy,
        "below": img_h - cy,
        "left": cx,
        "right": img_w - cx,
    }
    return max(distances, key=distances.get)
