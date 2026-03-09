"""Image file handler — processes standalone image files (PNG, JPG, etc.)."""

from __future__ import annotations

from pathlib import Path

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
) -> Path:
    """Remove watermark from a single image file.

    Args:
        input_path: Path to the source image.
        output_path: Path to write the cleaned image.
        config: Runtime configuration.
        annotation: Optional user hints about the watermark.
        force_strategy: Override the AI's strategy recommendation.

    Returns:
        Path to the output file.
    """
    image = Image.open(input_path)
    analysis = detect_watermark(image, config, annotation)
    cleaned = remove_watermark(image, analysis, config, force_strategy)

    # Convert back to RGB if saving as JPEG
    if output_path.suffix.lower() in (".jpg", ".jpeg"):
        cleaned = cleaned.convert("RGB")

    cleaned.save(output_path, quality=95)
    return output_path
