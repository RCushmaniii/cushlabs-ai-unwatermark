"""Watermark detection — layered approach for reliable results.

Detection priority:
1. OCR detection (deterministic, fast, local) — catches text watermarks
2. Florence-2 via Replicate (~$0.001/call) — catches logos, visual watermarks
3. Claude/GPT-4o Vision (fallback) — if no Replicate token available
4. Heuristic fallback — when no AI is available
"""

from __future__ import annotations

import logging

from PIL import Image

from unwatermark.config import Config
from unwatermark.core.analyzer import _heuristic_fallback, analyze_watermark
from unwatermark.core.florence_detector import detect_watermark_florence
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
    2. Florence-2 via Replicate — fast, cheap, handles logos and visual watermarks
    3. Claude/GPT-4o Vision — legacy fallback if no Replicate token
    4. Heuristic as last resort — when no AI is available

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
        logger.info("OCR found no text watermark — trying Florence-2")
    except Exception as e:
        logger.warning(f"OCR detection failed: {e} — trying Florence-2")

    # Layer 2: Florence-2 via Replicate (cheap, fast, handles visual watermarks)
    if config.has_replicate_token:
        try:
            # Build a detection prompt from user annotation if available
            detection_prompt = None
            if annotation and annotation.has_description:
                detection_prompt = annotation.description

            florence_result = detect_watermark_florence(
                image,
                replicate_api_token=config.replicate_api_token,
                detection_prompt=detection_prompt,
            )
            if florence_result is not None:
                logger.info(
                    f"Florence-2 detection succeeded: '{florence_result.description}' "
                    f"confidence={florence_result.confidence}"
                )
                return florence_result
            logger.info("Florence-2 found no watermark — trying legacy AI")
        except Exception as e:
            logger.warning(f"Florence-2 detection failed: {e} — trying legacy AI")

    # Layer 3: Claude/GPT-4o Vision (legacy fallback — expensive, non-deterministic)
    if config.use_ai and config.can_use_ai:
        logger.info("Using Claude/GPT-4o Vision (legacy fallback)")
        return analyze_watermark(image, config, annotation)

    # Layer 4: Heuristic fallback
    return _heuristic_fallback(image, annotation)
