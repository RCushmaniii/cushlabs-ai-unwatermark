"""Watermark region detection.

Analyzes images to find watermark regions, with a default assumption of
bottom-right placement (common for NotebookLM, stock photo sites, etc.).
"""

from dataclasses import dataclass

import numpy as np
from PIL import Image


@dataclass
class WatermarkRegion:
    """Bounding box for a detected watermark area."""

    x: int
    y: int
    width: int
    height: int

    @property
    def x2(self) -> int:
        return self.x + self.width

    @property
    def y2(self) -> int:
        return self.y + self.height


def detect_watermark_region(
    image: Image.Image,
    position: str = "bottom-right",
    width_ratio: float = 0.25,
    height_ratio: float = 0.06,
) -> WatermarkRegion:
    """Detect the watermark region in an image.

    For now this uses a heuristic approach based on known watermark placements.
    The default targets NotebookLM-style watermarks in the bottom-right corner.

    Args:
        image: PIL Image to analyze.
        position: Where the watermark is expected. One of:
            "bottom-right", "bottom-left", "bottom-center",
            "top-right", "top-left", "top-center".
        width_ratio: Fraction of image width the watermark occupies (0.0-1.0).
        height_ratio: Fraction of image height the watermark occupies (0.0-1.0).

    Returns:
        WatermarkRegion with the detected bounding box.
    """
    img_w, img_h = image.size
    wm_w = int(img_w * width_ratio)
    wm_h = int(img_h * height_ratio)

    positions = {
        "bottom-right": (img_w - wm_w, img_h - wm_h),
        "bottom-left": (0, img_h - wm_h),
        "bottom-center": ((img_w - wm_w) // 2, img_h - wm_h),
        "top-right": (img_w - wm_w, 0),
        "top-left": (0, 0),
        "top-center": ((img_w - wm_w) // 2, 0),
    }

    if position not in positions:
        raise ValueError(f"Unknown position '{position}'. Use one of: {list(positions.keys())}")

    x, y = positions[position]
    return WatermarkRegion(x=x, y=y, width=wm_w, height=wm_h)


def detect_watermark_auto(image: Image.Image, threshold: float = 30.0) -> WatermarkRegion | None:
    """Attempt automatic watermark detection by finding low-variance edge regions.

    Scans the borders of the image for regions that look like overlaid watermarks
    (semi-transparent text/logos tend to reduce local variance compared to natural content).

    Args:
        image: PIL Image to analyze.
        threshold: Variance threshold below which a region is suspicious.

    Returns:
        WatermarkRegion if a candidate is found, None otherwise.
    """
    arr = np.array(image.convert("L"), dtype=np.float32)
    img_h, img_w = arr.shape

    # Scan bottom strip
    strip_h = int(img_h * 0.08)
    bottom_strip = arr[img_h - strip_h :, :]

    # Slide a window across the bottom strip to find anomalous regions
    window_w = int(img_w * 0.25)
    step = window_w // 4
    best_score = float("inf")
    best_x = 0

    for x in range(0, img_w - window_w, step):
        window = bottom_strip[:, x : x + window_w]
        # Compare local variance to neighbors above
        above = arr[img_h - 2 * strip_h : img_h - strip_h, x : x + window_w]
        diff = abs(float(np.std(window)) - float(np.std(above)))
        if diff < best_score:
            best_score = diff
            best_x = x

    if best_score < threshold:
        return WatermarkRegion(x=best_x, y=img_h - strip_h, width=window_w, height=strip_h)

    return None
