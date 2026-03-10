"""PPTX file handler — processes PowerPoint files with embedded watermarked images.

Targets the common case: slides that are each a single full-size PNG image
(e.g., exported from NotebookLM) with a watermark baked into the image.
"""

from __future__ import annotations

import io
import logging
from pathlib import Path
from typing import Callable

from PIL import Image
from pptx import Presentation

from unwatermark.config import Config
from unwatermark.core.detector import detect_watermark
from unwatermark.core.remover import remove_watermark
from unwatermark.models.annotation import UserAnnotation

logger = logging.getLogger(__name__)


def process_pptx(
    input_path: Path,
    output_path: Path,
    config: Config,
    annotation: UserAnnotation | None = None,
    force_strategy: str | None = None,
    on_progress: Callable[[str, int], None] | None = None,
) -> Path:
    """Remove watermarks from all images embedded in a PPTX file.

    Args:
        input_path: Path to the source PPTX.
        output_path: Path to write the cleaned PPTX.
        config: Runtime configuration.
        annotation: Optional user hints about the watermark.
        force_strategy: Override the AI's strategy recommendation.
        on_progress: Callback(message, percent) for progress updates.

    Returns:
        Path to the output file.
    """
    MAX_SLIDES = 20

    prs = Presentation(str(input_path))

    slide_count = len(prs.slides)
    if slide_count > MAX_SLIDES:
        raise ValueError(
            f"PPTX has {slide_count} slides (max {MAX_SLIDES}). "
            f"Split the file or use the CLI for larger presentations."
        )

    for slide_idx, slide in enumerate(prs.slides):
        pct = int(5 + (slide_idx / slide_count) * 90)
        if on_progress:
            on_progress(
                f"Processing slide {slide_idx + 1} of {slide_count}\u2026",
                pct,
            )

        for shape in slide.shapes:
            if not shape.shape_type or not hasattr(shape, "image"):
                continue

            try:
                image_wrapper = shape.image
            except Exception:
                continue

            image_bytes = image_wrapper.blob
            content_type = image_wrapper.content_type
            image = Image.open(io.BytesIO(image_bytes))
            logger.info(
                f"Slide {slide_idx + 1}: found image {image.width}x{image.height} "
                f"({content_type})"
            )

            analysis = detect_watermark(image, config, annotation)
            logger.info(
                f"Slide {slide_idx + 1}: watermark_found={analysis.watermark_found}, "
                f"confidence={analysis.confidence}, strategy={analysis.strategy.value}"
            )
            if not analysis.watermark_found:
                continue

            cleaned = remove_watermark(image, analysis, config, force_strategy)

            buf = io.BytesIO()
            img_format = _content_type_to_format(content_type)
            if img_format == "JPEG":
                cleaned = cleaned.convert("RGB")
            cleaned.save(buf, format=img_format, quality=95)

            # CRITICAL: shape.image returns a wrapper object — setting _blob on it
            # does NOT persist. We must update the actual ImagePart in the package
            # by navigating through the slide's relationship to the embedded image.
            actual_part = _get_image_part(shape, slide)
            if actual_part is not None:
                new_blob = buf.getvalue()
                actual_part._blob = new_blob
                logger.info(
                    f"Slide {slide_idx + 1}: replaced blob ({len(new_blob)} bytes)"
                )
            else:
                logger.warning(f"Slide {slide_idx + 1}: image part not found")

    if on_progress:
        on_progress("Saving presentation\u2026", 95)

    prs.save(str(output_path))

    if on_progress:
        on_progress("Done", 100)

    return output_path


def _get_image_part(shape, slide):
    """Get the actual ImagePart from the PPTX package for a picture shape.

    shape.image returns a read-only wrapper — to persist changes, we need
    the real ImagePart stored in the slide's relationships.
    """
    try:
        pic = shape._element
        ns_r = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
        ns_a = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
        blips = pic.findall(f".//{ns_a}blip")
        if not blips:
            return None
        r_embed = blips[0].get(f"{ns_r}embed")
        if not r_embed:
            return None
        return slide.part.related_part(r_embed)
    except Exception as e:
        logger.warning(f"Failed to resolve image part: {e}")
        return None


def _content_type_to_format(content_type: str) -> str:
    mapping = {
        "image/png": "PNG",
        "image/jpeg": "JPEG",
        "image/gif": "GIF",
        "image/bmp": "BMP",
        "image/tiff": "TIFF",
    }
    return mapping.get(content_type, "PNG")
