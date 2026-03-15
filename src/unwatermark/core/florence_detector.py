"""Florence-2 watermark detection via Replicate API.

Uses Microsoft's Florence-2 vision foundation model for watermark detection.
Two strategies:
1. Caption to Phrase Grounding — describe the image, then locate "watermark"
2. OCR with Region — find all text with bounding boxes (catches text watermarks
   that EasyOCR missed, like rotated or semi-transparent text)

This is the v2 detection layer — replaces Claude Vision as the AI fallback
when EasyOCR finds no text watermarks. ~$0.001/call (~1000x cheaper than Claude).
"""

from __future__ import annotations

import io
import base64
import json
import logging
import re

from PIL import Image

from unwatermark.models.analysis import (
    BackgroundType,
    RemovalStrategy,
    SurroundingContext,
    WatermarkAnalysis,
    WatermarkRegion,
)

logger = logging.getLogger(__name__)

# Known watermark text patterns (same as ocr_detector but used for Florence OCR results)
_WATERMARK_PATTERNS = [
    r"\bnotebooklm\b", r"\bshutterstock\b", r"\bgetty\s*images?\b",
    r"\bistock\b", r"\badobe\s*stock\b", r"\bdreamstime\b", r"\b123rf\b",
    r"\balamy\b", r"\bcanva\b", r"\bfreepik\b", r"\benvato\b",
    r"\bmade\s+with\b", r"\bcreated\s+(?:with|by)\b", r"\bpowered\s+by\b",
    r"\bsample\b", r"\bpreview\b", r"\bwatermark\b", r"\bdraft\b",
    r"\bproof\b", r"\bcomposite\b", r"\bcopyright\b", r"\u00a9",
    r"www\.\w+\.\w+",
]


def detect_watermark_florence(
    image: Image.Image,
    replicate_api_token: str | None = None,
    detection_prompt: str | None = None,
    max_bbox_percent: float = 15.0,
) -> WatermarkAnalysis | None:
    """Detect watermarks using Florence-2 via Replicate.

    Tries two approaches:
    1. Caption to Phrase Grounding — asks Florence-2 to find "watermark" regions
    2. OCR with Region — finds text, checks against watermark patterns

    Args:
        image: PIL Image to analyze.
        replicate_api_token: Replicate API token (uses env var if None).
        detection_prompt: Custom prompt for what to look for.
        max_bbox_percent: Maximum bbox size as % of image area (filter false positives).

    Returns:
        WatermarkAnalysis if watermark detected, None if nothing found.
    """
    import replicate

    if replicate_api_token:
        client = replicate.Client(api_token=replicate_api_token)
    else:
        client = replicate.Client()

    img_w, img_h = image.size
    img_uri = _image_to_data_uri(image)

    # Strategy 1: Caption to Phrase Grounding
    # First get a caption, then ground "watermark" in it
    api_errors = []
    result = _try_grounding(client, img_uri, img_w, img_h, max_bbox_percent, detection_prompt, api_errors)
    if result is not None:
        return result

    # Strategy 2: OCR with Region — find text and check against watermark patterns
    result = _try_ocr_with_region(client, img_uri, img_w, img_h, max_bbox_percent, detection_prompt, api_errors)
    if result is not None:
        return result

    # If API calls failed (not just "no watermark found"), raise so the
    # circuit breaker in detector.py can disable Florence-2 for this session.
    if api_errors:
        raise RuntimeError(f"Florence-2 API errors: {api_errors[0]}")

    logger.info("Florence-2: no watermarks detected")
    return None


def _try_grounding(
    client, img_uri: str, img_w: int, img_h: int,
    max_bbox_percent: float, custom_prompt: str | None,
    api_errors: list | None = None,
) -> WatermarkAnalysis | None:
    """Try Caption to Phrase Grounding to find watermark regions."""
    try:
        # First, get a detailed caption
        logger.info("Florence-2: getting image caption...")
        caption_output = client.run(
            "lucataco/florence-2-large:da53547e17d45b9cfb48174b2f18af8b83ca020fa76db62136bf9c6616762595",
            input={
                "image": img_uri,
                "task_input": "More Detailed Caption",
            },
        )
        caption = _extract_text(caption_output)
        if not caption:
            return None

        logger.info(f"Florence-2 caption: {caption[:100]}...")

        # Check if caption mentions watermark-related terms
        caption_lower = caption.lower()
        has_watermark_mention = any(
            term in caption_lower
            for term in ["watermark", "logo", "overlay", "text overlay", "stamp", "copyright"]
        )

        if not has_watermark_mention and not custom_prompt:
            logger.info("Florence-2: caption doesn't mention watermarks")
            return None

        # Ground the watermark mention in the image
        ground_text = custom_prompt or "watermark"
        logger.info(f"Florence-2: grounding '{ground_text}'...")
        ground_output = client.run(
            "lucataco/florence-2-large:da53547e17d45b9cfb48174b2f18af8b83ca020fa76db62136bf9c6616762595",
            input={
                "image": img_uri,
                "task_input": "Caption to Phrase Grounding",
                "text_input": ground_text if custom_prompt else caption,
            },
        )

        return _parse_grounding_output(ground_output, img_w, img_h, max_bbox_percent, "watermark")

    except Exception as e:
        logger.warning(f"Florence-2 grounding failed: {e}")
        if api_errors is not None:
            api_errors.append(str(e))
        return None


def _try_ocr_with_region(
    client, img_uri: str, img_w: int, img_h: int,
    max_bbox_percent: float, custom_prompt: str | None,
    api_errors: list | None = None,
) -> WatermarkAnalysis | None:
    """Try OCR with Region to find text watermarks Florence might catch that EasyOCR missed."""
    try:
        logger.info("Florence-2: running OCR with region...")
        ocr_output = client.run(
            "lucataco/florence-2-large:da53547e17d45b9cfb48174b2f18af8b83ca020fa76db62136bf9c6616762595",
            input={
                "image": img_uri,
                "task_input": "OCR with Region",
            },
        )

        return _parse_ocr_output(ocr_output, img_w, img_h, max_bbox_percent, custom_prompt)

    except Exception as e:
        logger.warning(f"Florence-2 OCR failed: {e}")
        if api_errors is not None:
            api_errors.append(str(e))
        return None


def _image_to_data_uri(image: Image.Image) -> str:
    """Convert PIL Image to a base64 data URI for Replicate API."""
    buf = io.BytesIO()
    image.convert("RGB").save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{b64}"


def _extract_text(output) -> str:
    """Extract text from Replicate output (may be string, dict, iterator, etc)."""
    if isinstance(output, str):
        return output
    if isinstance(output, dict):
        # Replicate Florence-2 returns {'img': None, 'text': "..."}
        if "text" in output:
            return str(output["text"])
        for key in ["caption", "result"]:
            if key in output:
                return str(output[key])
        return str(output)
    if hasattr(output, '__iter__'):
        return "".join(str(p) for p in output)
    return str(output)


def _parse_florence_dict(text: str) -> dict | None:
    """Parse Florence-2's text output which is a Python dict repr, not JSON.

    Florence returns strings like: "{'<OCR_WITH_REGION>': {'quad_boxes': [...], 'labels': [...]}}"
    This is a Python literal, not valid JSON (uses single quotes).
    """
    import ast
    try:
        return ast.literal_eval(text)
    except (ValueError, SyntaxError):
        pass

    # Try JSON as fallback
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    return None


def _parse_grounding_output(
    output, img_w: int, img_h: int, max_bbox_percent: float, label: str,
) -> WatermarkAnalysis | None:
    """Parse Caption to Phrase Grounding output for watermark bounding boxes."""
    text = _extract_text(output)
    if not text:
        return None

    # Try to parse as dict (Florence returns Python repr, not JSON)
    data = _parse_florence_dict(text)

    if data is None:
        # Florence grounding output may contain bbox coordinates in text format
        # Try to extract bounding boxes from text like "<loc_123><loc_456>..."
        return _parse_loc_tags(text, img_w, img_h, max_bbox_percent, label)

    if isinstance(data, dict):
        for key in data:
            val = data[key]
            if isinstance(val, dict) and "bboxes" in val:
                bboxes = val["bboxes"]
                labels = val.get("labels", [label] * len(bboxes))
                return _select_best_bbox(bboxes, labels, img_w, img_h, max_bbox_percent)

    return None


def _parse_ocr_output(
    output, img_w: int, img_h: int, max_bbox_percent: float,
    custom_prompt: str | None,
) -> WatermarkAnalysis | None:
    """Parse OCR with Region output for watermark text."""
    text = _extract_text(output)
    if not text:
        return None

    data = _parse_florence_dict(text)
    if not isinstance(data, dict):
        return None

    # Florence OCR with Region returns quad_boxes and labels
    for key in data:
        val = data[key]
        if not isinstance(val, dict):
            continue

        quad_boxes = val.get("quad_boxes", [])
        labels = val.get("labels", [])

        if not quad_boxes or not labels:
            continue

        # Find watermark text among OCR results
        img_area = img_w * img_h
        for i, (quad, label) in enumerate(zip(quad_boxes, labels)):
            label_lower = label.lower().strip()

            # Check word count — watermarks are short
            if len(label_lower.split()) > 5:
                continue

            is_watermark = False

            # Check custom prompt
            if custom_prompt:
                for word in custom_prompt.lower().split():
                    if len(word) >= 3 and word in label_lower:
                        is_watermark = True
                        break

            # Check known patterns
            if not is_watermark:
                for pattern in _WATERMARK_PATTERNS:
                    if re.search(pattern, label_lower):
                        is_watermark = True
                        break

            if not is_watermark:
                continue

            # Convert quad to bbox
            xs = quad[0::2]
            ys = quad[1::2]
            x = int(min(xs))
            y = int(min(ys))
            w = int(max(xs) - min(xs))
            h = int(max(ys) - min(ys))

            # Size filter
            area = w * h
            pct = (area / img_area) * 100
            if pct > max_bbox_percent or w < 5 or h < 5:
                continue

            # Add padding + icon expansion
            pad_x = max(5, int(img_w * 0.01))
            pad_y = max(5, int(img_h * 0.015))
            icon_margin = max(20, int(w * 0.5))

            expanded_x = max(0, x - icon_margin)
            expanded_w = w + icon_margin + pad_x
            region = WatermarkRegion(x=expanded_x, y=y, width=expanded_w, height=h)
            padded = region.padded_xy(0, pad_y, img_w, img_h)

            logger.info(
                f"Florence-2 OCR: found watermark '{label}' at ({x},{y},{w}x{h})"
            )

            return WatermarkAnalysis(
                watermark_found=True,
                region=padded,
                description=f"Florence-2 OCR: '{label}'",
                background_type=BackgroundType.MIXED,
                strategy=RemovalStrategy.INPAINT,
                confidence=0.85,
                reasoning=f"Florence-2 OCR detected watermark text '{label}'",
                context=SurroundingContext(),
                clone_direction=_best_clone_direction(x, y, w, h, img_w, img_h),
            )

    return None


def _parse_loc_tags(
    text: str, img_w: int, img_h: int, max_bbox_percent: float, label: str,
) -> WatermarkAnalysis | None:
    """Parse Florence-2 location tags like <loc_123> from text output."""
    # Florence sometimes returns coordinates as <loc_XXX> tags
    loc_pattern = r"<loc_(\d+)>"
    locs = [int(m) for m in re.findall(loc_pattern, text)]

    if len(locs) < 4:
        return None

    # Locations are normalized to 0-999, need to scale to image dimensions
    bboxes = []
    for i in range(0, len(locs) - 3, 4):
        x1 = int(locs[i] / 999 * img_w)
        y1 = int(locs[i + 1] / 999 * img_h)
        x2 = int(locs[i + 2] / 999 * img_w)
        y2 = int(locs[i + 3] / 999 * img_h)
        bboxes.append([x1, y1, x2, y2])

    return _select_best_bbox(bboxes, [label] * len(bboxes), img_w, img_h, max_bbox_percent)


def _select_best_bbox(
    bboxes: list, labels: list, img_w: int, img_h: int, max_bbox_percent: float,
) -> WatermarkAnalysis | None:
    """Select the best bounding box from Florence-2 detections."""
    img_area = img_w * img_h

    for i, bbox in enumerate(bboxes):
        x1, y1, x2, y2 = [int(v) for v in bbox[:4]]
        w = x2 - x1
        h = y2 - y1
        area = w * h
        pct = (area / img_area) * 100
        label = labels[i] if i < len(labels) else "watermark"

        if pct > max_bbox_percent or w < 5 or h < 5:
            continue

        # Add padding
        pad_x = max(5, int(img_w * 0.01))
        pad_y = max(5, int(img_h * 0.015))
        region = WatermarkRegion(x=x1, y=y1, width=w, height=h)
        padded = region.padded_xy(pad_x, pad_y, img_w, img_h)

        logger.info(
            f"Florence-2 grounding: found '{label}' at ({x1},{y1},{w}x{h}) = {pct:.1f}%"
        )

        return WatermarkAnalysis(
            watermark_found=True,
            region=padded,
            description=f"Florence-2 detected: '{label}'",
            background_type=BackgroundType.MIXED,
            strategy=RemovalStrategy.INPAINT,
            confidence=0.85,
            reasoning=f"Florence-2 phrase grounding found '{label}' ({pct:.1f}% of image)",
            context=SurroundingContext(),
            clone_direction=_best_clone_direction(x1, y1, w, h, img_w, img_h),
        )

    return None


def _best_clone_direction(
    x: int, y: int, w: int, h: int, img_w: int, img_h: int,
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
