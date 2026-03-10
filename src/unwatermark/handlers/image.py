"""Image file handler — processes standalone image files (PNG, JPG, etc.)."""

from __future__ import annotations

from pathlib import Path
from typing import Callable

from PIL import Image

from unwatermark.config import Config
from unwatermark.core.multipass import clean_image
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

    if on_progress:
        on_progress("Removing watermarks\u2026", 30)

    result = clean_image(image, config, annotation, force_strategy)

    if output_path.suffix.lower() in (".jpg", ".jpeg"):
        result.image = result.image.convert("RGB")

    if on_progress:
        on_progress("Saving cleaned image\u2026", 90)

    result.image.save(output_path, quality=95)

    if on_progress:
        msg = f"Done — removed {result.removed} watermark{'s' if result.removed != 1 else ''}"
        on_progress(msg, 100)

    return output_path
