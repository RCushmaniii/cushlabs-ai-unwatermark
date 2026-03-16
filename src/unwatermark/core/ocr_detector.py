"""OCR-based watermark detection — deterministic, fast, local.

Uses EasyOCR to find text overlays in images. Unlike vision LLMs, this
produces the same result every time for the same input. It catches text
watermarks like "NotebookLM", "Shutterstock", "Getty Images", etc.

This is the primary detection layer. The AI vision model (Claude/GPT-4o)
is only used as a fallback when OCR finds nothing (logo watermarks, etc.).
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass

import numpy as np
from PIL import Image

from unwatermark.models.analysis import (
    BackgroundType,
    RemovalStrategy,
    SurroundingContext,
    WatermarkAnalysis,
    WatermarkRegion,
)

logger = logging.getLogger(__name__)

# Common watermark text patterns (case-insensitive).
# These are strong signals — if OCR finds any of these, it's almost
# certainly a watermark, even if it's in the middle of the image.
_WATERMARK_PATTERNS = [
    r"notebooklm",
    r"shutterstock",
    r"getty\s*images?",
    r"istock\s*photo",
    r"adobe\s*stock",
    r"dream(?:s)?time",
    r"123rf",
    r"alamy",
    r"deposit\s*photos?",
    r"fotolia",
    r"bigstock",
    r"canva",
    r"unsplash",
    r"pexels",
    r"pixabay",
    r"freepik",
    r"envato",
    r"made\s+with\b",
    r"created\s+(?:with|by|in)\b",
    r"powered\s+by\b",
    r"generated\s+(?:with|by)\b",
    r"\bsample\b",
    r"\bpreview\b",
    r"\bwatermark\b",
    r"\bdraft\b",
    r"\bproof\b",
    r"\bcomposite\b",
    r"\bcomp\s+image\b",
    r"\bfor\s+review\s+only\b",
    r"\bnot\s+for\s+(?:re)?sale\b",
    r"\bcopyright\s*\u00a9?",
    r"\u00a9\s*\d{4}",
    r"www\.\w+\.\w+",
]

# Fail-fast import check — if easyocr isn't installed, importing this
# module should raise ImportError so callers know OCR is unavailable.
import easyocr as _easyocr_module  # noqa: F401

# Lazy-loaded EasyOCR reader (heavy initialization — only do it once)
_reader = None


def _get_reader():
    """Get or create the EasyOCR reader (lazy singleton)."""
    global _reader
    if _reader is None:
        import easyocr
        logger.info("Initializing EasyOCR reader (first use)...")
        _reader = easyocr.Reader(["en"], gpu=False, verbose=False)
        logger.info("EasyOCR reader ready")
    return _reader


@dataclass
class OCRDetection:
    """A single text detection from OCR."""

    text: str
    bbox: tuple[int, int, int, int]  # x, y, width, height
    confidence: float
    is_watermark_text: bool  # matches known watermark patterns
    is_edge_position: bool  # in typical watermark position (corners/edges)


def detect_watermark_ocr(
    image: Image.Image,
    known_text: str | None = None,
) -> WatermarkAnalysis | None:
    """Detect text watermarks using OCR.

    Args:
        image: PIL Image to scan.
        known_text: Optional hint about what the watermark says (from user annotation).

    Returns:
        WatermarkAnalysis if a watermark is detected, None if no text watermark found.
        Returns None (not watermark_found=False) so the caller knows to try AI detection.
    """
    reader = _get_reader()
    img_w, img_h = image.size

    # Boost contrast before OCR — semi-transparent watermarks are too faint
    # for EasyOCR at normal contrast (5-15 levels on 0-255).
    # 3x enhancement makes watermark text readable without hurting content text.
    from PIL import ImageEnhance
    enhanced = ImageEnhance.Contrast(image).enhance(3.0)
    img_array = np.array(enhanced.convert("RGB"))

    # EasyOCR returns list of (bbox, text, confidence)
    # bbox is [[x1,y1], [x2,y1], [x2,y2], [x1,y2]] (polygon corners)
    results = reader.readtext(img_array)

    if not results:
        logger.info("OCR: no text found in image")
        return None

    # Score each detection
    detections: list[OCRDetection] = []
    for bbox_poly, text, conf in results:
        # Convert polygon to bounding rect
        xs = [p[0] for p in bbox_poly]
        ys = [p[1] for p in bbox_poly]
        x = int(min(xs))
        y = int(min(ys))
        w = int(max(xs) - min(xs))
        h = int(max(ys) - min(ys))

        # Check if text matches watermark patterns
        is_wm_text = _is_watermark_text(text, known_text)

        # Check if position is typical for watermarks (edges/corners)
        is_edge = _is_edge_position(x, y, w, h, img_w, img_h)

        detections.append(OCRDetection(
            text=text,
            bbox=(x, y, w, h),
            confidence=conf,
            is_watermark_text=is_wm_text,
            is_edge_position=is_edge,
        ))

        logger.debug(
            f"OCR: '{text}' conf={conf:.2f} pos=({x},{y},{w}x{h}) "
            f"wm_text={is_wm_text} edge={is_edge}"
        )

    # Find the best watermark candidate
    watermark = _select_best_watermark(detections, img_w, img_h)
    if watermark is None:
        logger.info(
            f"OCR: found {len(detections)} text regions but none look like watermarks"
        )
        return None

    # Build the analysis result
    x, y, w, h = watermark.bbox

    # Watermark text often has an accompanying icon/logo to the left.
    # Extend the bounding box leftward by 50% of text width to capture it.
    # Also add a small vertical expansion and right padding.
    icon_margin = max(20, int(w * 0.5))
    pad_right = max(5, int(img_w * 0.01))
    pad_y = max(8, int(img_h * 0.015))

    expanded_x = max(0, x - icon_margin)
    expanded_w = w + icon_margin + pad_right
    region = WatermarkRegion(x=expanded_x, y=y, width=expanded_w, height=h)
    padded = region.padded_xy(0, pad_y, img_w, img_h)

    logger.info(
        f"OCR: detected watermark '{watermark.text}' at ({x},{y},{w}x{h}) "
        f"conf={watermark.confidence:.2f}"
    )

    return WatermarkAnalysis(
        watermark_found=True,
        region=padded,
        description=f"Text watermark: '{watermark.text}'",
        background_type=BackgroundType.MIXED,
        strategy=RemovalStrategy.INPAINT,
        confidence=min(0.95, watermark.confidence + 0.1),  # boost slightly — OCR is reliable
        reasoning=f"OCR detected text '{watermark.text}' in watermark-typical position",
        context=SurroundingContext(),
        clone_direction=_best_clone_direction(x, y, w, h, img_w, img_h),
    )


def _is_watermark_text(text: str, known_text: str | None = None) -> bool:
    """Check if detected text matches known watermark patterns."""
    lower = text.lower().strip()

    # Very short text is usually noise
    if len(lower) < 2:
        return False

    # Long text is almost certainly content, not a watermark.
    # Watermarks are typically 1-4 words. "© 2024 Getty Images" = 4 words.
    # "Field research requires a compromise between speed and" = 9 words = content.
    word_count = len(lower.split())
    if word_count > 5:
        return False

    # Check user-provided hint first
    if known_text:
        hint_lower = known_text.lower()
        # Fuzzy match — the OCR might get a few characters wrong
        hint_words = hint_lower.split()
        for word in hint_words:
            if len(word) >= 3 and word in lower:
                return True

    # Check against known watermark patterns
    for pattern in _WATERMARK_PATTERNS:
        if re.search(pattern, lower):
            return True

    # Fuzzy match against known brand names — OCR often garbles watermark text
    # because watermarks are semi-transparent. "Shutteri OEL:" → "shutterstock"
    if _fuzzy_brand_match(lower):
        return True

    return False


# Brand names for fuzzy matching — ONLY long names (8+ chars) to avoid
# false positives where random content words match short brands.
# Short brands (getty, istock, canva, alamy, etc.) are already handled
# by exact regex patterns above.
_KNOWN_BRANDS = [
    "shutterstock", "gettyimages", "istockphoto", "adobestock",
    "dreamstime", "depositphotos", "notebooklm",
]


def _fuzzy_brand_match(text: str, threshold: float = 0.65) -> bool:
    """Check if garbled OCR text is close enough to a known watermark brand.

    Uses character overlap ratio — what fraction of the brand's characters
    appear in the OCR text (order-independent). Handles OCR garbling like
    "Shutteri OEL:" -> "shutterstock" (overlap ratio ~0.7).
    """
    # Remove non-alphanumeric to normalize OCR artifacts
    cleaned = re.sub(r"[^a-z0-9]", "", text)
    if len(cleaned) < 3:
        return False

    for brand in _KNOWN_BRANDS:
        # Skip if lengths are too different (not the same word)
        if abs(len(cleaned) - len(brand)) > max(len(brand) * 0.4, 3):
            continue

        # Character overlap: how many of the brand's characters appear in the OCR text
        brand_chars = list(brand)
        text_chars = list(cleaned)
        matches = 0
        for c in brand_chars:
            if c in text_chars:
                matches += 1
                text_chars.remove(c)  # each char only counts once

        overlap = matches / len(brand)
        if overlap >= threshold:
            logger.debug(f"Fuzzy brand match: '{text}' -> '{brand}' (overlap={overlap:.2f})")
            return True

    return False


def _is_edge_position(
    x: int, y: int, w: int, h: int, img_w: int, img_h: int
) -> bool:
    """Check if a text region is in a typical watermark position.

    Watermarks are almost always in corners or along edges — rarely
    in the center of the image (unless they're diagonal repeating).
    """
    cx = x + w / 2
    cy = y + h / 2

    # Define edge zones: outer 20% of image on each side
    margin_x = img_w * 0.20
    margin_y = img_h * 0.20

    in_left = cx < margin_x
    in_right = cx > img_w - margin_x
    in_top = cy < margin_y
    in_bottom = cy > img_h - margin_y

    return in_left or in_right or in_top or in_bottom


def _select_best_watermark(
    detections: list[OCRDetection],
    img_w: int,
    img_h: int,
) -> OCRDetection | None:
    """Pick the most likely watermark from OCR detections.

    Scoring is designed so that a known watermark pattern match dominates.
    Without a pattern match, text needs very strong positional/size signals
    to be considered — this prevents content text like titles from triggering
    false positives.

    Scoring:
    - Known watermark text: +5.0 (dominant signal — almost always correct)
    - Edge/corner position: +1.0
    - Small relative size (< 5% of image area): +1.0
    - Short text (1-3 words): +0.5 (watermarks are brief, content is verbose)
    - OCR confidence: +0.0 to +1.0
    """
    if not detections:
        return None

    img_area = img_w * img_h
    scored: list[tuple[float, bool, OCRDetection]] = []

    for det in detections:
        score = 0.0
        _, _, w, h = det.bbox
        det_area = w * h
        has_pattern = det.is_watermark_text

        # Known watermark text is the dominant signal
        if has_pattern:
            score += 5.0

        # Typical watermark position (corners/edges)
        if det.is_edge_position:
            score += 1.0

        # Watermarks are small — tighter threshold than before
        if det_area < img_area * 0.05:
            score += 1.0
        elif det_area < img_area * 0.15:
            score += 0.3

        # Watermarks are typically short (1-3 words)
        word_count = len(det.text.strip().split())
        if 1 <= word_count <= 3:
            score += 0.5

        # OCR confidence
        score += det.confidence

        scored.append((score, has_pattern, det))

        logger.debug(
            f"OCR score: '{det.text}' = {score:.1f} "
            f"(pattern={has_pattern}, edge={det.is_edge_position}, "
            f"area={det_area/img_area*100:.1f}%)"
        )

    # Sort by score descending
    scored.sort(key=lambda x: x[0], reverse=True)

    best_score, best_has_pattern, best = scored[0]

    # Different thresholds depending on whether we have a pattern match.
    # With a pattern match (score >= 5.0 base), we're very confident.
    # Without a pattern match, require extremely strong signals to avoid
    # false positives on content text like titles or headings.
    if best_has_pattern:
        min_score = 5.0  # Pattern match alone is sufficient
    else:
        min_score = 4.5  # Without pattern, need edge + small + short + high conf

    if best_score < min_score:
        logger.debug(
            f"OCR: best candidate '{best.text}' scored {best_score:.1f} "
            f"(below threshold {min_score}, pattern={best_has_pattern})"
        )
        return None

    return best


def _best_clone_direction(
    x: int, y: int, w: int, h: int, img_w: int, img_h: int
) -> str:
    """Determine the best direction to clone from based on watermark position."""
    cx = x + w / 2
    cy = y + h / 2

    # Clone from the direction with the most space
    distances = {
        "above": cy,
        "below": img_h - cy,
        "left": cx,
        "right": img_w - cx,
    }
    return max(distances, key=distances.get)
