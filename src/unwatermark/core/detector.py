"""Watermark detection — layered approach for reliable results.

Detection priority:
1. OCR detection (deterministic, fast, local) — catches text watermarks
2. AI vision analysis (Claude/GPT-4o) — catches logos, non-text watermarks
3. Heuristic fallback — when no AI is available
"""

from __future__ import annotations

import logging

from PIL import Image

from unwatermark.config import Config
from unwatermark.core.analyzer import _heuristic_fallback, analyze_watermark
from unwatermark.core.ocr_detector import detect_watermark_ocr
from unwatermark.models.analysis import WatermarkAnalysis
from unwatermark.models.annotation import UserAnnotation

logger = logging.getLogger(__name__)


def detect_watermark(
    image: Image.Image,
    config: Config,
    annotation: UserAnnotation | None = None,
) -> WatermarkAnalysis:
    """Detect and analyze a watermark in an image.

    Uses a layered approach:
    1. OCR detection first — deterministic, catches text watermarks reliably
    2. AI vision as fallback — for logos, non-text overlays
    3. Heuristic as last resort — when AI is unavailable

    Args:
        image: PIL Image to analyze.
        config: Runtime config with API keys and provider selection.
        annotation: Optional user hints.

    Returns:
        WatermarkAnalysis with detection results and recommended strategy.
    """
    # Layer 1: OCR detection (deterministic, same result every time)
    known_text = None
    if annotation and annotation.has_description:
        known_text = annotation.description

    try:
        ocr_result = detect_watermark_ocr(image, known_text=known_text)
        if ocr_result is not None:
            logger.info(
                f"OCR detection succeeded: '{ocr_result.description}' "
                f"confidence={ocr_result.confidence}"
            )
            return ocr_result
        logger.info("OCR found no text watermark — trying AI detection")
    except Exception as e:
        logger.warning(f"OCR detection failed: {e} — trying AI detection")

    # Layer 2: AI vision analysis (non-deterministic but handles logos/non-text)
    if config.use_ai and config.can_use_ai:
        return analyze_watermark(image, config, annotation)

    # Layer 3: Heuristic fallback
    return _heuristic_fallback(image, annotation)
