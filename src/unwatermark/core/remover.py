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
) -> Image.Image | None:
    """Remove a watermark using the best available technique.

    Args:
        image: Source PIL Image.
        analysis: Watermark analysis results (from AI or heuristic).
        config: Runtime config for backend selection.
        force_strategy: Override the AI's strategy recommendation.

    Returns:
        New PIL Image with the watermark removed, or None if removal
        was skipped (e.g. region too large for safe inpainting).
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

    r = analysis.region

    # Safety guard: reject detections that cover too much of the image.
    # Large diagonal overlays (SAMPLE PREVIEW, DRAFT across full slide) can't
    # be safely inpainted — better to skip than destroy the image content.
    img_area = image.width * image.height
    wm_area = r.width * r.height
    coverage = wm_area / img_area if img_area > 0 else 0
    if coverage > 0.08 and force_strategy is None:
        logger.warning(
            f"Skipping removal: watermark region covers {coverage:.1%} of image "
            f"(>{8}% safety limit). Region=({r.x},{r.y},{r.width}x{r.height}), "
            f"desc='{analysis.description}'"
        )
        return None

    technique = get_technique(strategy, config)
    logger.info(
        f"Removing watermark: strategy={strategy.value}, technique={technique.name}, "
        f"region=({r.x},{r.y},{r.width}x{r.height}), image={image.width}x{image.height}"
    )
    return technique.remove(image, analysis.region, analysis)
