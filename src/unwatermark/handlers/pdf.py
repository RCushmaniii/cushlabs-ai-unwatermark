"""PDF file handler — extracts pages as images, removes watermarks, reassembles."""

from __future__ import annotations

import io
import logging
from pathlib import Path
from typing import Callable

import fitz  # PyMuPDF
from PIL import Image

from unwatermark.config import Config
from unwatermark.core.multipass import clean_image
from unwatermark.models.analysis import WatermarkAnalysis
from unwatermark.models.annotation import UserAnnotation

logger = logging.getLogger(__name__)


def process_pdf(
    input_path: Path,
    output_path: Path,
    config: Config,
    annotation: UserAnnotation | None = None,
    force_strategy: str | None = None,
    dpi: int = 200,
    on_progress: Callable[[str, int], None] | None = None,
) -> Path:
    """Remove watermarks from a PDF by rendering pages, cleaning, and reassembling.

    Uses multi-pass cleaning on each page to catch multiple watermarks.

    Args:
        input_path: Path to the source PDF.
        output_path: Path to write the cleaned PDF.
        config: Runtime configuration.
        annotation: Optional user hints about the watermark.
        force_strategy: Override the AI's strategy recommendation.
        dpi: Resolution for rendering PDF pages to images.
        on_progress: Callback(message, percent) for progress updates.

    Returns:
        Path to the output file.
    """
    MAX_PAGES = 20

    src_doc = fitz.open(str(input_path))
    out_doc = fitz.open()

    page_count = len(src_doc)
    if page_count > MAX_PAGES:
        src_doc.close()
        raise ValueError(
            f"PDF has {page_count} pages (max {MAX_PAGES}). "
            f"Split the file or use the CLI for larger documents."
        )

    zoom = dpi / 72.0
    matrix = fitz.Matrix(zoom, zoom)
    baseline_analysis: WatermarkAnalysis | None = None

    for page_idx in range(page_count):
        page_num = page_idx + 1
        # Each page gets a slice of the 5-93% progress range
        page_start_pct = int(5 + (page_idx / page_count) * 88)
        page_end_pct = int(5 + ((page_idx + 1) / page_count) * 88)

        if on_progress:
            on_progress(
                f"Page {page_num}/{page_count}: rendering...", page_start_pct
            )

        page = src_doc[page_idx]
        pix = page.get_pixmap(matrix=matrix)

        image = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)

        # Create a sub-progress callback that prefixes messages with page info
        # and maps clean_image's 10-95% range into this page's slice
        def _make_page_progress(pg_num: int, pg_total: int, start: int, end: int):
            def _page_progress(msg: str, inner_pct: int) -> None:
                if on_progress:
                    # Map inner_pct (10-95) into our page's range (start-end)
                    scaled = start + int((inner_pct - 10) / 85 * (end - start))
                    scaled = max(start, min(end, scaled))
                    on_progress(f"Page {pg_num}/{pg_total}: {msg}", scaled)
            return _page_progress

        page_progress = _make_page_progress(page_num, page_count, page_start_pct, page_end_pct) if on_progress else None

        result = clean_image(
            image, config, annotation, force_strategy,
            baseline=baseline_analysis,
            on_progress=page_progress,
        )

        if baseline_analysis is None and result.first_analysis is not None:
            baseline_analysis = result.first_analysis

        if on_progress:
            if result.removed > 0:
                on_progress(
                    f"Page {page_num}/{page_count}: removed {result.removed} watermark{'s' if result.removed != 1 else ''}",
                    page_end_pct,
                )
            else:
                on_progress(f"Page {page_num}/{page_count}: clean", page_end_pct)

        cleaned = result.image.convert("RGB")

        buf = io.BytesIO()
        cleaned.save(buf, format="JPEG", quality=95)
        buf.seek(0)

        img_doc = fitz.open(stream=buf.read(), filetype="jpeg")
        rect = page.rect
        out_page = out_doc.new_page(width=rect.width, height=rect.height)
        out_page.insert_image(rect, stream=img_doc.tobytes())
        img_doc.close()

    if on_progress:
        on_progress("Assembling PDF...", 95)

    out_doc.save(str(output_path))
    out_doc.close()
    src_doc.close()

    if on_progress:
        on_progress("Done", 100)

    return output_path
