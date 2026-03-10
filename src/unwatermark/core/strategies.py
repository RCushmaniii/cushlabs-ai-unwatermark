"""Strategy selection — maps analysis results to removal techniques."""

from __future__ import annotations

import logging

from unwatermark.models.analysis import (
    BackgroundType,
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

    strategy = analysis.strategy

    # When inpainting is available, prefer it for complex backgrounds
    # even if the AI recommended clone_stamp (inpaint is almost always better)
    if inpaint_available and analysis.background_type in (
        BackgroundType.COMPLEX_CONTENT,
        BackgroundType.MIXED,
        BackgroundType.SIMPLE_TEXTURE,
    ):
        strategy = RemovalStrategy.INPAINT

    # If inpainting was recommended but isn't available, fall back to clone stamp
    if strategy == RemovalStrategy.INPAINT and not inpaint_available:
        logger.warning("Inpaint requested but LaMa unavailable — using clone_stamp")
        strategy = RemovalStrategy.CLONE_STAMP

    return strategy
