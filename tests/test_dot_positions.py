"""Tests for dot position calculation module."""

import pytest
from reportlab.lib.units import cm, inch, mm

from dot_paper_generator._dot_positions import (
    center_cross_dots,
    compute_dot_positions,
    corner_marker_dots,
    grid_dots,
    resolve_points,
    to_points,
)


class TestToPoints:
    """Test unit conversion to ReportLab points."""

    @pytest.mark.parametrize(
        "unit,expected_factor",
        [
            ("in", inch),
            ("inch", inch),
            ("inches", inch),
            ("mm", mm),
            ("cm", cm),
            ("m", cm * 100),
            ("px", 1.0),
            ("pt", 1.0),
            ("point", 1.0),
            ("points", 1.0),
        ],
    )
    def test_unit_conversions(self, unit, expected_factor):
        """Test conversion for various units and aliases."""
        assert to_points(1.0, unit) == pytest.approx(expected_factor)

    def test_case_insensitive(self):
        """Test case-insensitive unit parsing."""
        assert to_points(1.0, "IN") == pytest.approx(inch)
        assert to_points(1.0, "MM") == pytest.approx(mm)

    def test_unknown_unit_raises_error(self):
        """Test that unknown units raise ValueError."""
        with pytest.raises(ValueError, match="Unknown unit"):
            to_points(1.0, "unknown")


class TestResolvePoints:
    """Test dimension resolution to points."""

    def test_all_in_inches(self):
        width_pts, height_pts, spacing_pts, margin_pts = resolve_points(
            page_width=8.5,
            page_height=11,
            unit="in",
            dot_spacing=0.2,
            dot_spacing_unit=None,
            margin=None,
            margin_unit=None,
        )
        assert width_pts == pytest.approx(8.5 * inch)
        assert height_pts == pytest.approx(11 * inch)
        assert spacing_pts == pytest.approx(0.2 * inch)
        assert margin_pts == pytest.approx(0.2 * inch)  # defaults to spacing

    def test_default_margin_equals_spacing(self):
        _, _, spacing_pts, margin_pts = resolve_points(
            page_width=8.5,
            page_height=11,
            unit="in",
            dot_spacing=0.25,
            dot_spacing_unit=None,
            margin=None,
            margin_unit=None,
        )
        assert margin_pts == pytest.approx(spacing_pts)

    def test_custom_margin(self):
        _, _, spacing_pts, margin_pts = resolve_points(
            page_width=8.5,
            page_height=11,
            unit="in",
            dot_spacing=0.2,
            dot_spacing_unit=None,
            margin=0.5,
            margin_unit=None,
        )
        assert margin_pts == pytest.approx(0.5 * inch)
        assert spacing_pts == pytest.approx(0.2 * inch)

    def test_mixed_units(self):
        width_pts, height_pts, spacing_pts, margin_pts = resolve_points(
            page_width=210,
            page_height=297,
            unit="mm",
            dot_spacing=5,
            dot_spacing_unit="mm",
            margin=1,
            margin_unit="cm",
        )
        assert width_pts == pytest.approx(210 * mm)
        assert height_pts == pytest.approx(297 * mm)
        assert spacing_pts == pytest.approx(5 * mm)
        assert margin_pts == pytest.approx(1 * cm)


class TestComputeDotPositions:
    """Test dot position calculation."""

    def test_grid_is_centered(self):
        """Test that grid is centered around (center_x, center_y)."""
        page_width = 8 * inch
        page_height = 8 * inch
        center_x, center_y = page_width / 2, page_height / 2
        spacing = 0.2 * inch
        margin = 0.5 * inch

        dots = compute_dot_positions(
            center_x, center_y, page_width, page_height, spacing, margin
        )

        # Center point should be in dots
        assert (center_x, center_y) in dots

    def test_dots_contain_grid_cross_and_corners(self):
        """Test that dots include grid, center cross, and corner markers."""
        page_width = 8 * inch
        page_height = 8 * inch
        center_x, center_y = page_width / 2, page_height / 2
        spacing = 0.2 * inch
        margin = 0.5 * inch

        dots = compute_dot_positions(
            center_x, center_y, page_width, page_height, spacing, margin
        )

        # Should have at least some dots from each component
        assert len(dots) > 100  # rough sanity check


class TestGridDots:
    """Test main grid dot generation."""

    def test_grid_centered_at_origin(self):
        """Test grid positioning around center."""
        center_x, center_y = 100, 100
        page_width, page_height = 400, 400
        spacing = 20
        margin = 10

        dots = grid_dots(center_x, center_y, page_width, page_height, spacing, margin)

        # Center should be included
        assert (center_x, center_y) in dots

        # Grid points should be multiples of spacing from center
        for dot_x, dot_y in dots:
            assert (
                abs((dot_x - center_x) % spacing) < 0.01
                or abs((dot_x - center_x) % spacing - spacing) < 0.01
            )
            assert (
                abs((dot_y - center_y) % spacing) < 0.01
                or abs((dot_y - center_y) % spacing - spacing) < 0.01
            )


class TestCenterCrossDots:
    """Test center cross marker dots."""

    def test_center_cross_at_center(self):
        """Test that center cross is at page center."""
        center_x, center_y = 100, 100
        page_width, page_height = 400, 400
        spacing = 20
        margin = 10

        dots = center_cross_dots(
            center_x, center_y, page_width, page_height, spacing, margin
        )

        # Should have dots at half-spacing from center
        half_spacing = spacing / 2
        assert (center_x - half_spacing, center_y) in dots or (
            center_x + half_spacing,
            center_y,
        ) in dots
        assert (center_x, center_y - half_spacing) in dots or (
            center_x,
            center_y + half_spacing,
        ) in dots


class TestCornerMarkerDots:
    """Test corner marker dots."""

    def test_corner_markers_exist(self):
        """Test that corner markers are generated."""
        center_x, center_y = 100, 100
        page_width, page_height = 400, 400
        spacing = 20

        dots = corner_marker_dots(center_x, center_y, page_width, page_height, spacing)

        # Should have some dots
        assert len(dots) > 0

        # All dots should be within page bounds
        for dot_x, dot_y in dots:
            assert 0 <= dot_x <= page_width
            assert 0 <= dot_y <= page_height
