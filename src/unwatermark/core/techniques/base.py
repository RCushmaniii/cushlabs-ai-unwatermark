"""Abstract base class for all removal techniques."""

from __future__ import annotations

from abc import ABC, abstractmethod

from PIL import Image

from unwatermark.models.analysis import WatermarkAnalysis, WatermarkRegion


class RemovalTechnique(ABC):
    """Interface that every removal technique implements."""

    @abstractmethod
    def remove(
        self,
        image: Image.Image,
        region: WatermarkRegion,
        analysis: WatermarkAnalysis,
    ) -> Image.Image:
        """Remove the watermark from the image.

        Args:
            image: Source PIL Image (should not be mutated — return a copy).
            region: The watermark bounding box.
            analysis: Full analysis context (background type, color, direction hints).

        Returns:
            New PIL Image with the watermark removed.
        """

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name for this technique."""
