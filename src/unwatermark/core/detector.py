"""Watermark detection — thin wrapper that routes to AI analyzer or heuristic fallback."""

from __future__ import annotations

from PIL import Image

from unwatermark.config import Config
from unwatermark.core.analyzer import analyze_watermark, _heuristic_fallback
from unwatermark.models.analysis import WatermarkAnalysis
from unwatermark.models.annotation import UserAnnotation


def detect_watermark(
    image: Image.Image,
    config: Config,
    annotation: UserAnnotation | None = None,
) -> WatermarkAnalysis:
    """Detect and analyze a watermark in an image.

    When AI is available, uses the vision LLM for intelligent detection.
    Falls back to position-based heuristic when AI is unavailable.

    Args:
        image: PIL Image to analyze.
        config: Runtime config with API keys and provider selection.
        annotation: Optional user hints.

    Returns:
        WatermarkAnalysis with detection results and recommended strategy.
    """
    if config.use_ai and config.can_use_ai:
        return analyze_watermark(image, config, annotation)
    return _heuristic_fallback(image, annotation)
