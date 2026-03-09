"""Watermark removal — routes analysis to the appropriate technique."""

from __future__ import annotations

from PIL import Image

from unwatermark.config import Config
from unwatermark.core.strategies import select_strategy
from unwatermark.core.techniques import get_technique
from unwatermark.core.techniques.lama_inpaint import is_lama_available
from unwatermark.models.analysis import WatermarkAnalysis


def remove_watermark(
    image: Image.Image,
    analysis: WatermarkAnalysis,
    config: Config | None = None,
    force_strategy: str | None = None,
) -> Image.Image:
    """Remove a watermark using the best available technique.

    Args:
        image: Source PIL Image.
        analysis: Watermark analysis results (from AI or heuristic).
        config: Runtime config for backend selection.
        force_strategy: Override the AI's strategy recommendation.

    Returns:
        New PIL Image with the watermark removed.
    """
    if not analysis.watermark_found:
        return image.copy()

    strategy = select_strategy(
        analysis,
        force_strategy=force_strategy,
        inpaint_available=is_lama_available(),
    )

    technique = get_technique(strategy, config)
    return technique.remove(image, analysis.region, analysis)
