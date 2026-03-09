"""PDF file handler — extracts pages as images, removes watermarks, reassembles."""

from __future__ import annotations

import io
from pathlib import Path

import fitz  # PyMuPDF
from PIL import Image

from unwatermark.config import Config
from unwatermark.core.detector import detect_watermark
from unwatermark.core.remover import remove_watermark
from unwatermark.models.annotation import UserAnnotation


def process_pdf(
    input_path: Path,
    output_path: Path,
    config: Config,
    annotation: UserAnnotation | None = None,
    force_strategy: str | None = None,
    dpi: int = 200,
) -> Path:
    """Remove watermarks from a PDF by rendering pages, cleaning, and reassembling.

    Each page is analyzed independently for optimal per-page strategy selection.

    Args:
        input_path: Path to the source PDF.
        output_path: Path to write the cleaned PDF.
        config: Runtime configuration.
        annotation: Optional user hints about the watermark.
        force_strategy: Override the AI's strategy recommendation.
        dpi: Resolution for rendering PDF pages to images.

    Returns:
        Path to the output file.
    """
    src_doc = fitz.open(str(input_path))
    out_doc = fitz.open()

    zoom = dpi / 72.0
    matrix = fitz.Matrix(zoom, zoom)

    for page_idx in range(len(src_doc)):
        page = src_doc[page_idx]
        pix = page.get_pixmap(matrix=matrix)

        image = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)

        analysis = detect_watermark(image, config, annotation)
        cleaned = remove_watermark(image, analysis, config, force_strategy)
        cleaned = cleaned.convert("RGB")

        buf = io.BytesIO()
        cleaned.save(buf, format="JPEG", quality=95)
        buf.seek(0)

        img_doc = fitz.open(stream=buf.read(), filetype="jpeg")
        rect = page.rect
        out_page = out_doc.new_page(width=rect.width, height=rect.height)
        out_page.insert_image(rect, stream=img_doc.tobytes())
        img_doc.close()

    out_doc.save(str(output_path))
    out_doc.close()
    src_doc.close()

    return output_path
