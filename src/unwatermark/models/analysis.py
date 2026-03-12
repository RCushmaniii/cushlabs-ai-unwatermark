"""Data models for watermark analysis and removal strategies."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PIL import Image


class BackgroundType(str, Enum):
    """What kind of content surrounds the watermark."""

    SOLID_COLOR = "solid_color"
    GRADIENT = "gradient"
    SIMPLE_TEXTURE = "simple_texture"
    COMPLEX_CONTENT = "complex_content"
    MIXED = "mixed"


class RemovalStrategy(str, Enum):
    """Which removal technique to use."""

    SOLID_FILL = "solid_fill"
    GRADIENT_FILL = "gradient_fill"
    CLONE_STAMP = "clone_stamp"
    INPAINT = "inpaint"

    @classmethod
    def from_background(cls, bg: BackgroundType) -> RemovalStrategy:
        """Select the best strategy for a given background type."""
        mapping = {
            BackgroundType.SOLID_COLOR: cls.SOLID_FILL,
            BackgroundType.GRADIENT: cls.GRADIENT_FILL,
            BackgroundType.SIMPLE_TEXTURE: cls.CLONE_STAMP,
            BackgroundType.COMPLEX_CONTENT: cls.INPAINT,
            BackgroundType.MIXED: cls.INPAINT,
        }
        return mapping[bg]


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

    def padded(self, padding: int, img_width: int, img_height: int) -> WatermarkRegion:
        """Return a new region expanded by padding, clamped to image bounds."""
        return self.padded_xy(padding, padding, img_width, img_height)

    def padded_xy(
        self, pad_x: int, pad_y: int, img_width: int, img_height: int
    ) -> WatermarkRegion:
        """Return a new region expanded by separate x/y padding, clamped to image bounds."""
        x = max(0, self.x - pad_x)
        y = max(0, self.y - pad_y)
        x2 = min(img_width, self.x2 + pad_x)
        y2 = min(img_height, self.y2 + pad_y)
        return WatermarkRegion(x=x, y=y, width=x2 - x, height=y2 - y)


@dataclass
class SurroundingContext:
    """Describes what's around the watermark in each direction."""

    above: str = ""
    below: str = ""
    left: str = ""
    right: str = ""


@dataclass
class WatermarkAnalysis:
    """Complete analysis result from the vision LLM or heuristic detector."""

    watermark_found: bool
    region: WatermarkRegion
    description: str = ""
    background_type: BackgroundType = BackgroundType.MIXED
    background_color: str | None = None
    strategy: RemovalStrategy = RemovalStrategy.CLONE_STAMP
    confidence: float = 0.5
    reasoning: str = ""
    context: SurroundingContext = field(default_factory=SurroundingContext)
    clone_direction: str = "above"
    mask: Image.Image | None = None  # Pixel-perfect mask from SAM (white=watermark, black=keep)
