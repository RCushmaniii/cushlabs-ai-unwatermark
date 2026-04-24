"""Template-based watermark detection for known watermarks (NotebookLM).

For watermarks that are always the same logo/text — like Google NotebookLM's
branding that appears on every slide it generates — template matching is vastly
more accurate than general-purpose AI detection:
- Deterministic: same input produces the same result every time
- Free: zero API calls
- Fast: ~50ms on a 1080p image
- Pixel-perfect mask: derived from the template's own pixels, not a padded bbox

Uses OpenCV normalized cross-correlation (TM_CCOEFF_NORMED) with multi-scale
matching so the watermark is found reliably across varying slide resolutions.
"""

from __future__ import annotations

import logging
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

from unwatermark.models.analysis import (
    BackgroundType,
    RemovalStrategy,
    WatermarkAnalysis,
    WatermarkRegion,
)

logger = logging.getLogger(__name__)

_TEMPLATES_DIR = Path(__file__).parent.parent / "assets"

# Minimum normalized cross-correlation score for a valid match (0.0-1.0).
# 0.65 is practical for anti-aliased text templates against real-world slide
# backgrounds — the mean-subtracting CCOEFF metric tolerates modest background
# variation. False positives are suppressed primarily by the bottom-right
# search-zone restriction, not by a tight threshold.
_MATCH_THRESHOLD = 0.65

# Template scale factors to search. PPTX renders the watermark at a slightly
# different pixel size than the reference screenshot (e.g., a 1665px source
# template matched at scale 0.826 on a 1376px-rendered slide). A 0.05-step
# sweep from 0.5 to 2.0 ensures we hit the real scale without gaps — the
# previous (0.15-step) sweep straddled the sweet spot and missed matches.
_SCALES = tuple(round(0.5 + 0.05 * i, 2) for i in range(31))  # 0.50 ... 2.00

# NotebookLM watermarks are always rendered in the bottom-right corner of the
# generated slide — never the middle, never the left side. Constraining the
# search to that quadrant eliminates false positives on unrelated text that
# happens to have similar cross-correlation (headings, bullet points, etc.)
# which previously caused content-damaging inpaints in the middle of slides.
# These fractions define the minimum x/y (as a fraction of image size) where
# the match *top-left corner* can land.
_SEARCH_X_MIN_FRAC = 0.60
_SEARCH_Y_MIN_FRAC = 0.80

# Templates live inside the distributed package (src/unwatermark/assets/).
_TEMPLATE_SPECS: tuple[tuple[str, str, str], ...] = (
    ("notebooklm_dark", "notebooklm_watermark_dark.png", "dark_bg"),
    ("notebooklm_light", "notebooklm_watermark_light.png", "light_bg"),
)

# Module-level cache — templates are loaded once per process.
_template_cache: list[tuple[str, np.ndarray, np.ndarray]] | None = None


def _load_templates() -> list[tuple[str, np.ndarray, np.ndarray]]:
    """Load and cache templates as (name, grayscale, pixel_mask) tuples.

    The pixel_mask is a binary mask of just the watermark glyphs (the text and
    logo strokes), derived from the template's brightness. This mask is what
    gets projected onto the source image to give LaMa a pixel-perfect removal
    target, instead of a loose bounding box that eats surrounding content.
    """
    global _template_cache
    if _template_cache is not None:
        return _template_cache

    templates: list[tuple[str, np.ndarray, np.ndarray]] = []
    for name, filename, bg_type in _TEMPLATE_SPECS:
        path = _TEMPLATES_DIR / filename
        if not path.exists():
            logger.warning(f"Template asset missing: {path}")
            continue

        img = cv2.imread(str(path), cv2.IMREAD_COLOR)
        if img is None:
            logger.warning(f"Failed to decode template: {path}")
            continue

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Derive the glyph mask from brightness:
        #   dark_bg variant  -> white text on dark background; bright pixels = glyph
        #   light_bg variant -> dark text on light background; dark pixels = glyph
        if bg_type == "dark_bg":
            _, mask = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY)
        else:
            _, mask = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY_INV)

        # Close small gaps in anti-aliased edges so the mask covers full strokes.
        kernel = np.ones((2, 2), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=1)

        templates.append((name, gray, mask))
        logger.info(f"Template loaded: {name} ({gray.shape[1]}x{gray.shape[0]})")

    _template_cache = templates
    return templates


def detect_watermark_template(image: Image.Image) -> WatermarkAnalysis | None:
    """Detect a known NotebookLM watermark via multi-scale template matching.

    Returns a WatermarkAnalysis with a pixel-perfect mask when a template
    matches above the confidence threshold. Returns None if nothing matches,
    so callers can fall through to the next detection layer (OCR, AI Vision).
    """
    templates = _load_templates()
    if not templates:
        return None

    img_arr = np.array(image.convert("RGB"))
    img_gray = cv2.cvtColor(img_arr, cv2.COLOR_RGB2GRAY)
    img_h, img_w = img_gray.shape

    # Crop to the bottom-right search zone before matching. NotebookLM
    # watermarks live only in this quadrant; searching elsewhere yields false
    # positives on unrelated text (bullets, headings) that happen to have
    # similar pixel structure.
    x_offset = int(img_w * _SEARCH_X_MIN_FRAC)
    y_offset = int(img_h * _SEARCH_Y_MIN_FRAC)
    search_region = img_gray[y_offset:img_h, x_offset:img_w]
    search_h, search_w = search_region.shape
    if search_h < 10 or search_w < 10:
        logger.info(
            f"Template matching: search zone too small ({search_w}x{search_h}) — skipping"
        )
        return None

    # Track the best match across all (template, scale) pairs.
    best: tuple[float, str, int, int, int, int, np.ndarray] | None = None

    for name, template_gray, template_mask in templates:
        t_h, t_w = template_gray.shape

        for scale in _SCALES:
            new_w = int(round(t_w * scale))
            new_h = int(round(t_h * scale))
            if new_w < 10 or new_h < 5:
                continue
            if new_w > search_w or new_h > search_h:
                continue

            scaled = cv2.resize(
                template_gray, (new_w, new_h), interpolation=cv2.INTER_AREA
            )
            scaled_mask = cv2.resize(
                template_mask, (new_w, new_h), interpolation=cv2.INTER_NEAREST
            )

            result = cv2.matchTemplate(search_region, scaled, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)

            if max_val >= _MATCH_THRESHOLD and (best is None or max_val > best[0]):
                # Translate search-region coordinates back into full-image coords.
                local_x, local_y = max_loc
                x = local_x + x_offset
                y = local_y + y_offset
                best = (float(max_val), name, x, y, new_w, new_h, scaled_mask)

    if best is None:
        logger.info("Template matching: no known watermark found")
        return None

    score, name, x, y, w, h, scaled_mask = best
    logger.info(
        f"Template matching: '{name}' at ({x},{y},{w}x{h}) score={score:.3f}"
    )

    # Project the template's pixel mask onto a full-image canvas at the match
    # location. Only actual glyph pixels are white — no bounding-box padding.
    full_mask = np.zeros((img_h, img_w), dtype=np.uint8)
    full_mask[y : y + h, x : x + w] = scaled_mask

    # Small dilation gives LaMa ~2px of halo around each stroke for clean
    # reconstruction, while still being far tighter than a full-bbox mask.
    dilate_kernel = np.ones((3, 3), np.uint8)
    full_mask = cv2.dilate(full_mask, dilate_kernel, iterations=2)

    mask_pil = Image.fromarray(full_mask, mode="L")

    return WatermarkAnalysis(
        watermark_found=True,
        region=WatermarkRegion(x=x, y=y, width=w, height=h),
        description=f"NotebookLM watermark ({name}) — template match",
        background_type=BackgroundType.MIXED,
        strategy=RemovalStrategy.INPAINT,
        confidence=score,
        reasoning=f"Template match score {score:.3f}",
        mask=mask_pil,
    )
