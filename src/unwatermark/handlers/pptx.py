"""PPTX file handler — processes PowerPoint files with embedded watermarked images.

Targets the common case: slides that are each a single full-size PNG image
(e.g., exported from NotebookLM) with a watermark baked into the image.
"""

from __future__ import annotations

import io
from pathlib import Path

from PIL import Image
from pptx import Presentation

from unwatermark.config import Config
from unwatermark.core.detector import detect_watermark
from unwatermark.core.remover import remove_watermark
from unwatermark.models.annotation import UserAnnotation


def process_pptx(
    input_path: Path,
    output_path: Path,
    config: Config,
    annotation: UserAnnotation | None = None,
    force_strategy: str | None = None,
) -> Path:
    """Remove watermarks from all images embedded in a PPTX file.

    Each slide image is analyzed independently — different slides may get
    different removal strategies based on their background content.

    Args:
        input_path: Path to the source PPTX.
        output_path: Path to write the cleaned PPTX.
        config: Runtime configuration.
        annotation: Optional user hints about the watermark.
        force_strategy: Override the AI's strategy recommendation.

    Returns:
        Path to the output file.
    """
    prs = Presentation(str(input_path))

    for slide in prs.slides:
        for shape in slide.shapes:
            if not shape.shape_type or not hasattr(shape, "image"):
                continue

            try:
                image_part = shape.image
            except Exception:
                continue

            image_bytes = image_part.blob
            image = Image.open(io.BytesIO(image_bytes))

            analysis = detect_watermark(image, config, annotation)
            if not analysis.watermark_found:
                continue

            cleaned = remove_watermark(image, analysis, config, force_strategy)

            buf = io.BytesIO()
            img_format = _content_type_to_format(image_part.content_type)
            if img_format == "JPEG":
                cleaned = cleaned.convert("RGB")
            cleaned.save(buf, format=img_format, quality=95)

            image_part._blob = buf.getvalue()

    prs.save(str(output_path))
    return output_path


def _content_type_to_format(content_type: str) -> str:
    mapping = {
        "image/png": "PNG",
        "image/jpeg": "JPEG",
        "image/gif": "GIF",
        "image/bmp": "BMP",
        "image/tiff": "TIFF",
    }
    return mapping.get(content_type, "PNG")
