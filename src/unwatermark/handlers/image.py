"""Image file handler — processes standalone image files (PNG, JPG, etc.)."""

from pathlib import Path

from PIL import Image

from unwatermark.core.detector import detect_watermark_region
from unwatermark.core.remover import remove_watermark


def process_image(
    input_path: Path,
    output_path: Path,
    position: str = "bottom-right",
    width_ratio: float = 0.25,
    height_ratio: float = 0.06,
) -> Path:
    """Remove watermark from a single image file.

    Args:
        input_path: Path to the source image.
        output_path: Path to write the cleaned image.
        position: Watermark position hint.
        width_ratio: Fraction of image width the watermark occupies.
        height_ratio: Fraction of image height the watermark occupies.

    Returns:
        Path to the output file.
    """
    image = Image.open(input_path)
    region = detect_watermark_region(image, position, width_ratio, height_ratio)
    cleaned = remove_watermark(image, region)

    # Convert back to RGB if saving as JPEG
    if output_path.suffix.lower() in (".jpg", ".jpeg"):
        cleaned = cleaned.convert("RGB")

    cleaned.save(output_path, quality=95)
    return output_path
