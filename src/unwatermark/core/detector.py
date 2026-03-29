"""Watermark detection — layered approach for reliable results.

v2 Detection pipeline:
1. OCR detection (deterministic, fast, local — optional on lightweight deploys)
2. Florence-2 via Replicate (~$0.001/call) — catches text + visual watermarks
   → SAM refinement (~$0.003) — pixel-perfect mask for precise inpainting
3. Grounded SAM standalone (~$0.003) — combined detection + masking fallback
4. Claude/GPT-4o Vision (legacy fallback) — expensive, non-deterministic
5. Heuristic fallback — when no AI is available
"""

from __future__ import annotations

import logging

from PIL import Image

from unwatermark.config import AnalysisProvider, Config
from unwatermark.core.analyzer import _heuristic_fallback, analyze_watermark
from unwatermark.core.florence_detector import detect_watermark_florence
from unwatermark.core.sam_detector import detect_watermark_sam, refine_with_sam
from unwatermark.models.analysis import WatermarkAnalysis
from unwatermark.models.annotation import UserAnnotation

# EasyOCR is optional — not available on lightweight deployments (e.g. Render free tier)
try:
    from unwatermark.core.ocr_detector import detect_watermark_ocr

    _HAS_EASYOCR = True
except ImportError:
    _HAS_EASYOCR = False

logger = logging.getLogger(__name__)

# Circuit breakers: after a Replicate model fails once, skip it for the session.
# Avoids wasting 10+ seconds per slide on repeated API errors.
_florence_disabled = False
_sam_disabled = False


def detect_watermark(
    image: Image.Image,
    config: Config,
    annotation: UserAnnotation | None = None,
    skip_vision_ai: bool = False,
) -> WatermarkAnalysis:
    """Detect and analyze a watermark in an image.

    v2 layered approach:
    1. OCR detection — deterministic, catches text watermarks (optional on deploy)
    2. Florence-2 → SAM refinement — detect + pixel-perfect mask
    3. Grounded SAM standalone — combined detection + masking fallback
    4. Claude/GPT-4o Vision — legacy fallback (skipped if skip_vision_ai=True)
    5. Heuristic as last resort

    Args:
        image: PIL Image to analyze.
        config: Runtime config with API keys and provider selection.
        annotation: Optional user hints.
        skip_vision_ai: If True, skip Claude/GPT-4o Vision (used in pass 2+).

    Returns:
        WatermarkAnalysis with detection results and recommended strategy.
    """
    global _florence_disabled, _sam_disabled

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
            logger.info("OCR found no text watermark — trying AI Vision")
        except Exception as e:
            logger.warning(f"OCR detection failed: {e} — trying AI Vision")
    else:
        logger.info("EasyOCR not installed — skipping to AI Vision")

    # NOTE: Florence-2 and Grounded SAM detection layers are disabled.
    # Claude Vision handles detection reliably, and the Replicate detection
    # models (Florence-2, SAM) consume rate limit budget that's better
    # reserved for LaMa inpainting — the one Replicate call that matters.
    # Re-enable when Replicate rate limits are no longer a constraint.

    # Layer 4: AI Vision — try primary provider, then fallback to secondary
    # Skipped on pass 2+ re-scans (skip_vision_ai=True) to save cost/time
    if not skip_vision_ai and config.use_ai and config.can_use_ai:
        logger.info(f"Using {config.analysis_provider.value} Vision")
        primary_result = analyze_watermark(image, config, annotation)

        if primary_result.watermark_found:
            # Refine AI Vision result with SAM too
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

    # Layer 5: Heuristic fallback
    return _heuristic_fallback(image, annotation)


def _try_sam_refinement(
    image: Image.Image,
    analysis: WatermarkAnalysis,
    config: Config,
) -> WatermarkAnalysis:
    """Attempt to refine a detection result with a SAM pixel-perfect mask.

    If SAM refinement succeeds, attaches the mask to the analysis.
    If it fails, returns the original analysis unchanged (rectangular mask fallback).
    """
    global _sam_disabled

    # Already has a pixel mask (e.g., from Grounded SAM standalone)
    if analysis.mask is not None:
        return analysis

    if not config.has_replicate_token or _sam_disabled:
        return analysis

    try:
        mask = refine_with_sam(
            image,
            analysis,
            replicate_api_token=config.replicate_api_token,
        )
        if mask is not None:
            analysis.mask = mask
            logger.info("SAM refinement: attached pixel-perfect mask")
        else:
            logger.info("SAM refinement: no mask produced — using rectangular fallback")
    except Exception as e:
        logger.warning(f"SAM refinement error: {e} — disabling for this session")
        _sam_disabled = True

    return analysis
