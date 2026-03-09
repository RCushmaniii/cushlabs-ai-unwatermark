"""User-provided annotation data for guiding watermark detection."""

from __future__ import annotations

from dataclasses import dataclass

from unwatermark.models.analysis import WatermarkRegion


@dataclass
class UserAnnotation:
    """User hints about the watermark — optional but improves accuracy."""

    description: str = ""
    region: WatermarkRegion | None = None

    @property
    def has_region(self) -> bool:
        return self.region is not None

    @property
    def has_description(self) -> bool:
        return bool(self.description.strip())
