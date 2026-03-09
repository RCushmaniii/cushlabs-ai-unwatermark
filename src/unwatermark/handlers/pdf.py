"""PDF file handler — extracts pages as images, removes watermarks, reassembles."""

import io
from pathlib import Path

import fitz  # PyMuPDF
from PIL import Image

from unwatermark.core.detector import detect_watermark_region
from unwatermark.core.remover import remove_watermark


def process_pdf(
    input_path: Path,
    output_path: Path,
    position: str = "bottom-right",
    width_ratio: float = 0.25,
    height_ratio: float = 0.06,
    dpi: int = 200,
) -> Path:
    """Remove watermarks from a PDF by rendering pages, cleaning, and reassembling.

    Each page is rendered to a high-res image, the watermark is removed,
    and a new PDF is built from the cleaned images.

    Args:
        input_path: Path to the source PDF.
        output_path: Path to write the cleaned PDF.
        position: Watermark position hint.
        width_ratio: Fraction of image width the watermark occupies.
        height_ratio: Fraction of image height the watermark occupies.
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

        # Convert PyMuPDF pixmap to PIL Image
        image = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)

        # Detect and remove watermark
        region = detect_watermark_region(image, position, width_ratio, height_ratio)
        cleaned = remove_watermark(image, region)
        cleaned = cleaned.convert("RGB")

        # Convert cleaned image back to a PDF page
        buf = io.BytesIO()
        cleaned.save(buf, format="JPEG", quality=95)
        buf.seek(0)

        img_doc = fitz.open(stream=buf.read(), filetype="jpeg")
        # Insert image as a page matching original page dimensions
        rect = page.rect
        out_page = out_doc.new_page(width=rect.width, height=rect.height)
        out_page.insert_image(rect, stream=img_doc.tobytes())
        img_doc.close()

    out_doc.save(str(output_path))
    out_doc.close()
    src_doc.close()

    return output_path
