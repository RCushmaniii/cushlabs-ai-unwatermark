"""Multi-pass watermark removal — detect and remove until clean.

After removing a watermark, re-scans the image for additional watermarks.
Handles cases like images with multiple overlapping watermarks (e.g., a
stock photo with both a tiled "Shutterstock" pattern and a corner logo).

Pass 1 uses the full detection stack (OCR → AI → heuristic).
Pass 2+ uses OCR only to avoid expensive/slow AI calls for each re-scan.
Caps at MAX_PASSES to prevent infinite loops.
"""

from __future__ import annotations

import gc
import logging
from dataclasses import dataclass

from PIL import Image

from unwatermark.config import Config
from unwatermark.core.detector import detect_watermark
from unwatermark.core.remover import remove_watermark
from unwatermark.models.analysis import WatermarkAnalysis
from unwatermark.models.annotation import UserAnnotation

# EasyOCR is optional — not available on lightweight deployments
try:
    from unwatermark.core.ocr_detector import detect_watermark_ocr

    _HAS_EASYOCR = True
except ImportError:
    _HAS_EASYOCR = False

logger = logging.getLogger(__name__)

MAX_PASSES = 3


@dataclass
class CleanResult:
    """Result of multi-pass cleaning."""

    image: Image.Image
    removed: int
    first_analysis: WatermarkAnalysis | None  # for use as baseline on other slides


def clean_image(
    image: Image.Image,
    config: Config,
    annotation: UserAnnotation | None = None,
    force_strategy: str | None = None,
    baseline: WatermarkAnalysis | None = None,
) -> CleanResult:
    """Remove all detectable watermarks from an image using multiple passes.

    Args:
        image: Source PIL Image.
        config: Runtime configuration.
        annotation: Optional user hints about the watermark.
        force_strategy: Override the AI's strategy recommendation.
        baseline: Optional baseline analysis to use when detection fails
                  (e.g., from a previous slide in a presentation).

    Returns:
        CleanResult with cleaned image, count of removals, and first analysis.
    """
    current = image
    removed = 0
    first_analysis: WatermarkAnalysis | None = None

    # Extract known_text hint for OCR from annotation
    known_text = None
    if annotation and annotation.has_description:
        known_text = annotation.description

    for pass_num in range(1, MAX_PASSES + 1):
        if pass_num == 1:
            # Full detection stack: OCR → AI → heuristic
            analysis = detect_watermark(current, config, annotation)
        else:
            # Subsequent passes: OCR only (fast, no API calls)
            # On lightweight deployments without EasyOCR, skip extra passes
            if not _HAS_EASYOCR:
                logger.info(f"Pass {pass_num}: EasyOCR not installed — skipping extra passes")
                break
            ocr_result = detect_watermark_ocr(current, known_text=known_text)
            if ocr_result is not None:
                analysis = ocr_result
            else:
                logger.info(f"Pass {pass_num}: no more text watermarks found — done")
                break

        if not analysis.watermark_found:
            # If first pass finds nothing but we have a baseline, use it
            if pass_num == 1 and baseline is not None:
                logger.info(f"Pass {pass_num}: no watermark found, using baseline")
                analysis = baseline
            else:
                logger.info(f"Pass {pass_num}: no more watermarks found — done")
                break

        # Save the first detection for use as baseline on other slides
        if first_analysis is None:
            first_analysis = analysis

        r = analysis.region
        logger.info(
            f"Pass {pass_num}: removing '{analysis.description}' "
            f"at ({r.x},{r.y},{r.width}x{r.height})"
        )

        current = remove_watermark(current, analysis, config, force_strategy)
        removed += 1

        # Free memory between passes — LaMa and OCR are memory-hungry
        gc.collect()

    if removed > 1:
        logger.info(f"Multi-pass complete: removed {removed} watermarks")

    return CleanResult(image=current, removed=removed, first_analysis=first_analysis)
