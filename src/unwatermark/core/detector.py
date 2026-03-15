"""Watermark detection — layered approach for reliable results.

Detection priority:
1. OCR detection (deterministic, fast, local) — catches text watermarks
2. Florence-2 via Replicate (~$0.001/call) — catches logos, visual watermarks
3. Claude/GPT-4o Vision (fallback) — expensive, non-deterministic
4. Heuristic fallback — when no AI is available
"""

from __future__ import annotations

import logging

from PIL import Image

from unwatermark.config import AnalysisProvider, Config
from unwatermark.core.analyzer import _heuristic_fallback, analyze_watermark
from unwatermark.core.florence_detector import detect_watermark_florence
from unwatermark.models.analysis import WatermarkAnalysis
from unwatermark.models.annotation import UserAnnotation

# EasyOCR is optional — not available on lightweight deployments (e.g. Render free tier)
try:
    from unwatermark.core.ocr_detector import detect_watermark_ocr

    _HAS_EASYOCR = True
except ImportError:
    _HAS_EASYOCR = False

logger = logging.getLogger(__name__)

# Circuit breaker: after Florence-2 fails once, skip it for the rest of the session.
# Avoids wasting 10+ seconds per slide on repeated Replicate API errors.
_florence_disabled = False


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
    # Skipped on lightweight deployments where EasyOCR/PyTorch aren't installed
    known_text = None
    if annotation and annotation.has_description:
        known_text = annotation.description

    if _HAS_EASYOCR:
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
    else:
        logger.info("EasyOCR not installed — skipping to Florence-2")

    # Layer 2: Florence-2 via Replicate (cheap, fast, handles visual watermarks)
    global _florence_disabled
    if config.has_replicate_token and not _florence_disabled:
        try:
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
            logger.info("Florence-2 found no watermark — trying AI Vision")
        except Exception as e:
            logger.warning(f"Florence-2 failed: {e} — disabling for this session")
            _florence_disabled = True

    # Layer 3: AI Vision — try primary provider, then fallback to secondary
    if config.use_ai and config.can_use_ai:
        logger.info(f"Using {config.analysis_provider.value} Vision")
        primary_result = analyze_watermark(image, config, annotation)

        # If primary provider found a watermark, use it
        if primary_result.watermark_found:
            return primary_result

        # If primary says no watermark AND isn't very confident, try the OTHER
        # provider as second opinion. Skip if primary is confident (>= 0.85) —
        # the secondary can hallucinate watermarks on clean images.
        if (
            config.analysis_provider == AnalysisProvider.CLAUDE
            and config.has_openai_key
            and primary_result.confidence < 0.85
        ):
            logger.info("Claude found no watermark — trying GPT-4o as second opinion")
            from unwatermark.config import Config as _Cfg
            secondary_config = _Cfg(
                openai_api_key=config.openai_api_key,
                analysis_provider=AnalysisProvider.OPENAI,
                analysis_model="gpt-4o",
                use_ai=True,
            )
            try:
                secondary_result = analyze_watermark(image, secondary_config, annotation)
                if secondary_result.watermark_found:
                    logger.info(
                        f"GPT-4o found watermark: '{secondary_result.description}'"
                    )
                    return secondary_result
            except Exception as e:
                logger.warning(f"GPT-4o fallback failed: {e}")
        elif (
            config.analysis_provider == AnalysisProvider.OPENAI
            and config.has_anthropic_key
            and primary_result.confidence < 0.85
        ):
            logger.info("GPT-4o found no watermark — trying Claude as second opinion")
            from unwatermark.config import Config as _Cfg
            secondary_config = _Cfg(
                anthropic_api_key=config.anthropic_api_key,
                analysis_provider=AnalysisProvider.CLAUDE,
                analysis_model="claude-sonnet-4-20250514",
                use_ai=True,
            )
            try:
                secondary_result = analyze_watermark(image, secondary_config, annotation)
                if secondary_result.watermark_found:
                    logger.info(
                        f"Claude found watermark: '{secondary_result.description}'"
                    )
                    return secondary_result
            except Exception as e:
                logger.warning(f"Claude fallback failed: {e}")

        return primary_result

    # Layer 4: Heuristic fallback
    return _heuristic_fallback(image, annotation)
