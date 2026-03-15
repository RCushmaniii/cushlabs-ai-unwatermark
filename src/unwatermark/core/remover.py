"""Watermark removal — routes analysis to the appropriate technique."""

from __future__ import annotations

import logging

from PIL import Image

from unwatermark.config import Config
from unwatermark.core.strategies import select_strategy
from unwatermark.core.techniques import get_technique
from unwatermark.core.techniques.lama_inpaint import is_lama_available
from unwatermark.models.analysis import RemovalStrategy, WatermarkAnalysis

logger = logging.getLogger(__name__)


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
        logger.warning(
            "Watermark not detected — returning original image unchanged. "
            "Try adding a description of the watermark to improve detection."
        )
        return image.copy()

    strategy = select_strategy(
        analysis,
        force_strategy=force_strategy,
        inpaint_available=is_lama_available(),
    )

    # Auto-select alpha subtraction for large semi-transparent overlays.
    # When the watermark region covers >5% of the image area, it's likely
    # a semi-transparent overlay (diagonal SAMPLE PREVIEW, large Shutterstock)
    # that alpha subtraction handles better than inpainting.
    r = analysis.region
    if strategy == RemovalStrategy.INPAINT and force_strategy is None:
        img_area = image.width * image.height
        wm_area = r.width * r.height
        coverage = wm_area / img_area if img_area > 0 else 0
        desc_lower = (analysis.description or "").lower()
        # Keywords alone aren't enough — require minimum 3% coverage to avoid
        # routing tiny corner watermarks to alpha subtraction.
        has_overlay_keywords = (
            "diagonal" in desc_lower
            or "semi-transparent" in desc_lower
            or "faint" in desc_lower
        )
        is_likely_overlay = (
            coverage > 0.05
            or (has_overlay_keywords and coverage > 0.03)
        )
        if is_likely_overlay:
            logger.info(
                f"Auto-switching to alpha subtraction: "
                f"coverage={coverage:.1%}, desc='{analysis.description[:60]}'"
            )
            strategy = RemovalStrategy.ALPHA_SUBTRACT

    technique = get_technique(strategy, config)
    logger.info(
        f"Removing watermark: strategy={strategy.value}, technique={technique.name}, "
        f"region=({r.x},{r.y},{r.width}x{r.height}), image={image.width}x{image.height}"
    )
    return technique.remove(image, analysis.region, analysis)
