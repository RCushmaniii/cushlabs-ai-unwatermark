"""Strategy selection — maps analysis results to removal techniques."""

from __future__ import annotations

import logging

from unwatermark.models.analysis import (
    RemovalStrategy,
    WatermarkAnalysis,
)

logger = logging.getLogger(__name__)


def select_strategy(
    analysis: WatermarkAnalysis,
    force_strategy: str | None = None,
    inpaint_available: bool = True,
) -> RemovalStrategy:
    """Choose the best removal strategy based on analysis results.

    When LaMa inpainting is available, it's preferred for complex_content and
    mixed backgrounds since it produces far better results than clone_stamp.
    For solid_color and gradient backgrounds, simpler techniques are used since
    they're faster and produce clean results.

    Args:
        analysis: The watermark analysis from AI or heuristic detector.
        force_strategy: If set, override the AI's recommendation.
        inpaint_available: Whether LaMa inpainting is installed/available.

    Returns:
        The RemovalStrategy to use.
    """
    if force_strategy:
        return RemovalStrategy(force_strategy)

    # When LaMa is available, ALWAYS use it — it produces the best results
    # across all background types. Solid fill and clone stamp leave visible
    # artifacts on anything other than perfectly uniform backgrounds.
    if inpaint_available:
        return RemovalStrategy.INPAINT

    # Fallback when LaMa is not installed
    strategy = analysis.strategy
    if strategy == RemovalStrategy.INPAINT:
        logger.warning("Inpaint requested but LaMa unavailable — using clone_stamp")
        strategy = RemovalStrategy.CLONE_STAMP

    return strategy
