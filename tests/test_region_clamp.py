"""Unit tests for WatermarkRegion.clamped().

Locks in the bounds-clamp behavior that protects every PIL crop call from
PIL's "Coordinate 'lower' is less than 'upper'" rejection when a detector
or user-drawn box lands outside the image.
"""

from __future__ import annotations

from PIL import Image

from unwatermark.models.analysis import WatermarkRegion


class TestClamped:
    def test_inside_bounds_unchanged(self):
        r = WatermarkRegion(x=10, y=20, width=100, height=50).clamped(800, 600)
        assert (r.x, r.y, r.width, r.height) == (10, 20, 100, 50)

    def test_overflow_right_clamps_width(self):
        r = WatermarkRegion(x=700, y=10, width=200, height=50).clamped(800, 600)
        assert r.x == 700
        assert r.width == 100  # 800 - 700
        assert r.x2 == 800

    def test_overflow_bottom_clamps_height(self):
        r = WatermarkRegion(x=10, y=550, width=50, height=200).clamped(800, 600)
        assert r.y == 550
        assert r.height == 50  # 600 - 550
        assert r.y2 == 600

    def test_negative_origin_pulled_to_zero(self):
        r = WatermarkRegion(x=-30, y=-20, width=100, height=80).clamped(800, 600)
        assert r.x == 0 and r.y == 0
        assert r.width == 70 and r.height == 60

    def test_fully_outside_right_collapses_to_zero(self):
        r = WatermarkRegion(x=1000, y=10, width=50, height=20).clamped(800, 600)
        assert r.width == 0  # fully outside; consumers should skip

    def test_fully_outside_bottom_collapses_to_zero(self):
        r = WatermarkRegion(x=10, y=900, width=50, height=20).clamped(800, 600)
        assert r.height == 0

    def test_clamped_box_is_pil_safe(self):
        """The whole point: PIL.crop must accept the clamped box without raising."""
        img = Image.new("RGB", (800, 600), color=(255, 255, 255))
        # Originally would have left=10, upper=550, right=60, lower=750 — lower
        # exceeds image height so a naive clamp of just x2/y2 (without raising
        # x1/y1) would invert the box. clamped() keeps it valid.
        r = WatermarkRegion(x=10, y=550, width=50, height=200).clamped(800, 600)
        if r.width > 0 and r.height > 0:
            crop = img.crop((r.x, r.y, r.x2, r.y2))
            assert crop.size == (r.width, r.height)

    def test_clamped_with_x_beyond_width_is_pil_safe(self):
        """The actual Sentry case: r.x > image.width would invert the SAM crop."""
        img = Image.new("RGB", (800, 600), color=(255, 255, 255))
        r = WatermarkRegion(x=1500, y=10, width=50, height=20).clamped(800, 600)
        # Region collapses; consumer should skip — but the box is at least valid
        assert r.x <= r.x2 and r.y <= r.y2
