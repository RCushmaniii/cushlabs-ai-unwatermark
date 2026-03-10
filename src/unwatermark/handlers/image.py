"""Image file handler — processes standalone image files (PNG, JPG, etc.)."""

from __future__ import annotations

from pathlib import Path
from typing import Callable

from PIL import Image

from unwatermark.config import Config
from unwatermark.core.detector import detect_watermark
from unwatermark.core.remover import remove_watermark
from unwatermark.models.annotation import UserAnnotation


def process_image(
    input_path: Path,
    output_path: Path,
    config: Config,
    annotation: UserAnnotation | None = None,
    force_strategy: str | None = None,
    on_progress: Callable[[str, int], None] | None = None,
) -> Path:
    """Remove watermark from a single image file.

    Args:
        input_path: Path to the source image.
        output_path: Path to write the cleaned image.
        config: Runtime configuration.
        annotation: Optional user hints about the watermark.
        force_strategy: Override the AI's strategy recommendation.
        on_progress: Callback(message, percent) for progress updates.

    Returns:
        Path to the output file.
    """
    if on_progress:
        on_progress("Analyzing image for watermarks\u2026", 10)

    image = Image.open(input_path)
    analysis = detect_watermark(image, config, annotation)

    if on_progress:
        on_progress("Removing watermark\u2026", 50)

    cleaned = remove_watermark(image, analysis, config, force_strategy)

    if output_path.suffix.lower() in (".jpg", ".jpeg"):
        cleaned = cleaned.convert("RGB")

    if on_progress:
        on_progress("Saving cleaned image\u2026", 90)

    cleaned.save(output_path, quality=95)

    if on_progress:
        on_progress("Done", 100)

    return output_path
