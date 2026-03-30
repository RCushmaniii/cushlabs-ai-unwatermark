"""Multi-pass watermark removal — detect and remove until clean.

After removing a watermark, re-scans the image for additional watermarks.
Handles cases like images with multiple overlapping watermarks (e.g., a
stock photo with both a tiled "Shutterstock" pattern and a corner logo).

Pass 1 uses the full detection stack (OCR → Florence-2 → SAM → AI → heuristic).
Pass 2+ uses OCR + Florence-2/SAM (cheap, deterministic) but skips Claude/GPT-4o
Vision to avoid expensive non-deterministic calls on re-scans.
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

# Cap image dimensions to limit memory usage on constrained deployments.
# A 2048px image is ~12MB uncompressed vs ~35MB at 4000px — 3x savings that
# compound across multi-pass detection (base64 encoding, API uploads, masks).
MAX_IMAGE_DIMENSION = 2048


def constrain_image_size(image: Image.Image, max_dim: int = MAX_IMAGE_DIMENSION) -> Image.Image:
    """Downscale an image so its longest side is at most max_dim pixels.

    Returns the original image unchanged if already within bounds.
    Uses LANCZOS resampling for high-quality downscaling.
    """
    w, h = image.size
    if w <= max_dim and h <= max_dim:
        return image
    scale = max_dim / max(w, h)
    new_w = int(w * scale)
    new_h = int(h * scale)
    logger.info(f"Downscaling image from {w}x{h} to {new_w}x{new_h} (memory optimization)")
    return image.resize((new_w, new_h), Image.LANCZOS)


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
    current = constrain_image_size(image)
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
            # Subsequent passes: OCR + Florence-2/SAM (cheap, deterministic)
            # Skips Claude/GPT-4o Vision to avoid expensive re-scans
            _emit(on_progress, "Re-scanning for additional watermarks...", pass_base_pct)
            if _HAS_EASYOCR:
                ocr_result = detect_watermark_ocr(current, known_text=known_text)
                if ocr_result is not None:
                    analysis = ocr_result
                    _emit(
                        on_progress, f"Found: '{analysis.description}'", pass_base_pct + 5
                    )
                else:
                    logger.info(f"Pass {pass_num}: OCR found nothing on re-scan")
                    # On re-scan passes, only trust deterministic detectors
                    # (OCR, Florence-2, SAM). Do NOT fall through to the
                    # heuristic — it always "finds" something and causes
                    # unnecessary inpainting of clean areas.
                    if config.has_replicate_token:
                        analysis = detect_watermark(
                            current, config, annotation, skip_vision_ai=True
                        )
                        # Reject heuristic guesses on re-scans
                        if not analysis.watermark_found or "heuristic" in (analysis.description or "").lower():
                            logger.info(f"Pass {pass_num}: no more watermarks found — done")
                            break
                        _emit(
                            on_progress, f"Found: '{analysis.description}'", pass_base_pct + 5
                        )
                    else:
                        logger.info(f"Pass {pass_num}: no Florence-2/SAM available — done")
                        break
            else:
                # Lightweight deploy without EasyOCR: re-scan with full stack
                # but reject heuristic guesses to prevent blind inpainting.
                analysis = detect_watermark(current, config, annotation)
                if not analysis.watermark_found or "heuristic" in (analysis.description or "").lower():
                    logger.info(f"Pass {pass_num}: no more watermarks found — done")
                    break
                _emit(
                    on_progress, f"Found: '{analysis.description}'", pass_base_pct + 5
                )

        if not analysis.watermark_found:
            # Baseline is only useful for SAME watermark in SAME position across
            # slides (e.g., NotebookLM watermark at bottom-right on every slide).
            # Only apply if the baseline covers a small region (<10% of image) —
            # large baselines (diagonal overlays, tiled patterns) are too
            # slide-specific to reuse.
            if pass_num == 1 and baseline is not None:
                br = baseline.region
                img_area = current.width * current.height
                baseline_coverage = (br.width * br.height) / img_area if img_area > 0 else 1.0
                if baseline_coverage < 0.10:
                    logger.info(
                        f"Pass {pass_num}: no watermark found, using baseline "
                        f"(coverage={baseline_coverage:.1%})"
                    )
                    analysis = baseline
                    _emit(on_progress, f"Using baseline: '{analysis.description}'", pass_base_pct + 5)
                else:
                    logger.info(
                        f"Pass {pass_num}: no watermark found, baseline too large "
                        f"to reuse (coverage={baseline_coverage:.1%})"
                    )
                    break
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

        old_current = current
        result = remove_watermark(current, analysis, config, force_strategy)

        if result is None:
            # Removal was skipped (region too large for safe inpainting).
            # Don't re-scan — Vision AI will just find the same thing again.
            logger.info(
                f"Pass {pass_num}: removal skipped (region too large), "
                f"stopping multi-pass for this watermark"
            )
            break

        current = result
        # Explicitly free the pre-removal image so gc.collect() can reclaim it
        if old_current is not current:
            del old_current
        removed += 1

        # Free memory between passes — LaMa and OCR are memory-hungry
        gc.collect()

    # Targeted NotebookLM check: if the main loop found a different (larger)
    # watermark and never specifically found NotebookLM, do one targeted pass.
    # Skip if NotebookLM was already found and removed in the main loop.
    already_found_nbm = first_analysis is not None and "notebooklm" in (
        first_analysis.description or ""
    ).lower()

    _notebooklm_hint = UserAnnotation(
        description="NotebookLM watermark in the bottom-right corner"
    )
    if _HAS_EASYOCR:
        nbm_check = detect_watermark_ocr(current, known_text="NotebookLM")
    elif config.can_use_ai:
        nbm_check = detect_watermark(current, config, _notebooklm_hint)
        # Only accept if it specifically found NotebookLM (not another watermark)
        if nbm_check.watermark_found and "notebooklm" not in (
            nbm_check.description or ""
        ).lower():
            nbm_check = None
    else:
        nbm_check = None

    if not already_found_nbm and nbm_check is not None and nbm_check.watermark_found:
        r = nbm_check.region
        img_area = current.width * current.height
        nbm_coverage = (r.width * r.height) / img_area if img_area > 0 else 1.0

        # NotebookLM watermark is tiny (~100x20px = <0.5% of image).
        # If the detection region is larger than 3%, Claude Vision included
        # content text in the bounding box — reject to prevent damage.
        if nbm_coverage > 0.03:
            logger.warning(
                f"Targeted NotebookLM pass: region too large "
                f"({nbm_coverage:.1%} > 3%), skipping to prevent content damage. "
                f"Region=({r.x},{r.y},{r.width}x{r.height})"
            )
        else:
            logger.info(
                f"Targeted NotebookLM pass: found '{nbm_check.description}' "
                f"at ({r.x},{r.y},{r.width}x{r.height}) coverage={nbm_coverage:.1%}"
            )
            _emit(on_progress, "Removing NotebookLM watermark...", 90)
            result = remove_watermark(current, nbm_check, config, force_strategy)
            if result is not None:
                current = result
                removed += 1
                if first_analysis is None:
                    first_analysis = nbm_check
                gc.collect()

    if removed > 1:
        logger.info(f"Multi-pass complete: removed {removed} watermarks")

    _emit(on_progress, "Watermark removal complete", 95)

    return CleanResult(image=current, removed=removed, first_analysis=first_analysis)
