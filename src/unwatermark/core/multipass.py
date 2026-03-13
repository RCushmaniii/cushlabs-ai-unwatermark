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
from typing import TYPE_CHECKING

from PIL import Image

from unwatermark.config import Config
from unwatermark.core.detector import detect_watermark
from unwatermark.core.remover import remove_watermark
from unwatermark.models.analysis import WatermarkAnalysis
from unwatermark.models.annotation import UserAnnotation

if TYPE_CHECKING:
    from typing import Callable

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


def _emit(on_progress: Callable[[str, int], None] | None, msg: str, pct: int) -> None:
    """Safely emit a progress callback if one is provided."""
    if on_progress:
        on_progress(msg, pct)


def clean_image(
    image: Image.Image,
    config: Config,
    annotation: UserAnnotation | None = None,
    force_strategy: str | None = None,
    baseline: WatermarkAnalysis | None = None,
    on_progress: Callable[[str, int], None] | None = None,
) -> CleanResult:
    """Remove all detectable watermarks from an image using multiple passes.

    Args:
        image: Source PIL Image.
        config: Runtime configuration.
        annotation: Optional user hints about the watermark.
        force_strategy: Override the AI's strategy recommendation.
        baseline: Optional baseline analysis to use when detection fails
                  (e.g., from a previous slide in a presentation).
        on_progress: Optional callback(message, percent) for progress updates.

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
        # Scale progress percentage based on pass number:
        # Pass 1: 10-40, Pass 2: 40-65, Pass 3: 65-80
        pass_base_pct = 10 + (pass_num - 1) * 25

        if pass_num == 1:
            # Full detection stack: OCR → AI → heuristic
            _emit(on_progress, "Scanning for text watermarks...", pass_base_pct)
            analysis = detect_watermark(current, config, annotation)

            # Determine which layer detected the watermark for progress reporting
            if analysis.watermark_found:
                desc = analysis.description or ""
                if desc.startswith("Text watermark:"):
                    _emit(on_progress, f"Found: '{desc}'", pass_base_pct + 5)
                elif desc.startswith("Florence-2:") or "florence" in desc.lower():
                    _emit(on_progress, f"Found: '{desc}'", pass_base_pct + 5)
                else:
                    # AI vision or heuristic result
                    _emit(on_progress, f"Found: '{desc}'", pass_base_pct + 10)
        else:
            # Subsequent passes: OCR only (fast, no API calls)
            # On lightweight deployments without EasyOCR, skip extra passes
            _emit(on_progress, "Re-scanning for additional watermarks...", pass_base_pct)
            if not _HAS_EASYOCR:
                logger.info(f"Pass {pass_num}: EasyOCR not installed — skipping extra passes")
                break
            ocr_result = detect_watermark_ocr(current, known_text=known_text)
            if ocr_result is not None:
                analysis = ocr_result
                _emit(on_progress, f"Found: '{analysis.description}'", pass_base_pct + 5)
            else:
                logger.info(f"Pass {pass_num}: no more text watermarks found — done")
                break

        if not analysis.watermark_found:
            # If first pass finds nothing but we have a baseline, use it
            if pass_num == 1 and baseline is not None:
                logger.info(f"Pass {pass_num}: no watermark found, using baseline")
                analysis = baseline
                _emit(on_progress, f"Using baseline: '{analysis.description}'", pass_base_pct + 5)
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

        # Determine technique name for progress message
        technique_name = "inpainting"  # LaMa is the default/preferred technique
        removal_pct = pass_base_pct + 10
        _emit(on_progress, f"Removing watermark with {technique_name}...", removal_pct)

        current = remove_watermark(current, analysis, config, force_strategy)
        removed += 1

        # Free memory between passes — LaMa and OCR are memory-hungry
        gc.collect()

    # Final AI pass: if we removed watermarks via OCR but the full detection
    # stack wasn't exhausted on the last pass, run one more full-stack check.
    # This catches watermarks that OCR can't see (diagonal text, logos) but
    # that Claude/GPT-4o Vision can detect. Only runs if:
    #   1. We already removed at least one watermark (so there was a real watermark)
    #   2. AI detection is available (has API key)
    #   3. The first pass found something via OCR (meaning AI was never tried)
    if (
        removed > 0
        and config.use_ai
        and config.can_use_ai
        and first_analysis is not None
        and first_analysis.description.startswith("Text watermark:")  # OCR result
    ):
        final_pct = 80
        _emit(on_progress, "Final check for hidden watermarks...", final_pct)
        logger.info("Final pass: full-stack check for non-text watermarks (diagonal, logos)")
        final_analysis = detect_watermark(current, config, annotation)
        if final_analysis.watermark_found:
            r = final_analysis.region
            logger.info(
                f"Final pass: found '{final_analysis.description}' "
                f"at ({r.x},{r.y},{r.width}x{r.height})"
            )
            _emit(on_progress, f"Removing: '{final_analysis.description}'...", 85)
            current = remove_watermark(current, final_analysis, config, force_strategy)
            removed += 1
            gc.collect()
        else:
            logger.info("Final pass: no additional watermarks found")

    if removed > 1:
        logger.info(f"Multi-pass complete: removed {removed} watermarks")

    _emit(on_progress, "Watermark removal complete", 95)

    return CleanResult(image=current, removed=removed, first_analysis=first_analysis)
