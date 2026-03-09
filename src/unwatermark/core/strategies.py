"""Strategy selection — maps analysis results to removal techniques."""

from __future__ import annotations

from unwatermark.models.analysis import (
    BackgroundType,
    RemovalStrategy,
    WatermarkAnalysis,
)


def select_strategy(
    analysis: WatermarkAnalysis,
    force_strategy: str | None = None,
    inpaint_available: bool = True,
) -> RemovalStrategy:
    """Choose the best removal strategy based on analysis results.

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

    # If inpainting was recommended but isn't available, fall back to clone stamp
    if strategy == RemovalStrategy.INPAINT and not inpaint_available:
        strategy = RemovalStrategy.CLONE_STAMP

    return strategy
