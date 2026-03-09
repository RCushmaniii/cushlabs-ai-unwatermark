"""PPTX file handler — processes PowerPoint files with embedded watermarked images.

Targets the common case: slides that are each a single full-size PNG image
(e.g., exported from NotebookLM) with a watermark baked into the image.
"""

import io
from pathlib import Path

from PIL import Image
from pptx import Presentation
from pptx.util import Emu

from unwatermark.core.detector import detect_watermark_region
from unwatermark.core.remover import remove_watermark


def process_pptx(
    input_path: Path,
    output_path: Path,
    position: str = "bottom-right",
    width_ratio: float = 0.25,
    height_ratio: float = 0.06,
) -> Path:
    """Remove watermarks from all images embedded in a PPTX file.

    Iterates through every slide, finds image shapes, processes each image
    to remove the watermark, and replaces the image blob in-place.

    Args:
        input_path: Path to the source PPTX.
        output_path: Path to write the cleaned PPTX.
        position: Watermark position hint.
        width_ratio: Fraction of image width the watermark occupies.
        height_ratio: Fraction of image height the watermark occupies.

    Returns:
        Path to the output file.
    """
    prs = Presentation(str(input_path))
    images_processed = 0

    for slide_idx, slide in enumerate(prs.slides):
        for shape in slide.shapes:
            if not shape.shape_type or not hasattr(shape, "image"):
                continue

            try:
                image_part = shape.image
            except Exception:
                continue

            # Read the embedded image
            image_bytes = image_part.blob
            image = Image.open(io.BytesIO(image_bytes))

            # Detect and remove watermark
            region = detect_watermark_region(image, position, width_ratio, height_ratio)
            cleaned = remove_watermark(image, region)

            # Convert back to the original format
            buf = io.BytesIO()
            img_format = _content_type_to_format(image_part.content_type)
            if img_format == "JPEG":
                cleaned = cleaned.convert("RGB")
            cleaned.save(buf, format=img_format, quality=95)

            # Replace the image blob in the PPTX
            image_part._blob = buf.getvalue()
            images_processed += 1

    prs.save(str(output_path))
    return output_path


def _content_type_to_format(content_type: str) -> str:
    """Map MIME content type to PIL format string."""
    mapping = {
        "image/png": "PNG",
        "image/jpeg": "JPEG",
        "image/gif": "GIF",
        "image/bmp": "BMP",
        "image/tiff": "TIFF",
    }
    return mapping.get(content_type, "PNG")
