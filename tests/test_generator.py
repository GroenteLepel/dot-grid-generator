import pytest
from reportlab.lib.units import cm, inch, mm

from dot_paper_generator.generator import (
    _center_cross_dots,
    _compute_dot_positions,
    _corner_marker_dots,
    _grid_dots,
    _nearest_grid_coord,
    _resolve_points,
    _to_points,
    _within_margin,
    generate_dot_paper,
)


class TestToPoints:
    def test_inches(self):
        assert _to_points(1.0, "in") == pytest.approx(inch)

    def test_inch_alias(self):
        assert _to_points(1.0, "inch") == pytest.approx(inch)

    def test_inches_alias(self):
        assert _to_points(1.0, "inches") == pytest.approx(inch)

    def test_millimetres(self):
        assert _to_points(1.0, "mm") == pytest.approx(mm)

    def test_centimetres(self):
        assert _to_points(1.0, "cm") == pytest.approx(cm)

    def test_metres(self):
        assert _to_points(1.0, "m") == pytest.approx(cm * 100)

    def test_pixels_are_one_point(self):
        assert _to_points(1.0, "px") == pytest.approx(1.0)

    def test_pt(self):
        assert _to_points(1.0, "pt") == pytest.approx(1.0)

    def test_point_alias(self):
        assert _to_points(1.0, "point") == pytest.approx(1.0)

    def test_points_alias(self):
        assert _to_points(1.0, "points") == pytest.approx(1.0)

    def test_case_insensitive(self):
        assert _to_points(1.0, "IN") == pytest.approx(inch)
        assert _to_points(1.0, "MM") == pytest.approx(mm)
        assert _to_points(1.0, "Cm") == pytest.approx(cm)

    def test_scales_by_value(self):
        assert _to_points(2.5, "in") == pytest.approx(2.5 * inch)

    def test_unknown_unit_raises_value_error(self):
        with pytest.raises(ValueError, match="'furlong'"):
            _to_points(1.0, "furlong")

    def test_unknown_unit_message_lists_valid_options(self):
        with pytest.raises(ValueError, match="Valid options"):
            _to_points(1.0, "?")


class TestResolvePoints:
    def test_page_dimensions_are_converted_to_points(self):
        page_width_pts, page_height_pts, _, _ = _resolve_points(
            1.0, 2.0, "in", 0.2, None, None, None
        )
        assert page_width_pts == pytest.approx(inch)
        assert page_height_pts == pytest.approx(2 * inch)

    def test_dot_spacing_unit_override_is_independent_of_page_unit(self):
        _, _, spacing, _ = _resolve_points(6.32, 8.17, "in", 5.0, "mm", None, None)
        assert spacing == pytest.approx(5 * mm)

    def test_margin_none_inherits_spacing_value_and_unit(self):
        _, _, spacing, margin_pts = _resolve_points(
            1.0, 1.0, "in", 5.0, "mm", None, None
        )
        assert margin_pts == pytest.approx(spacing)

    def test_explicit_margin_is_converted_in_its_own_unit(self):
        _, _, _, margin_pts = _resolve_points(1.0, 1.0, "in", 0.2, None, 10.0, "mm")
        assert margin_pts == pytest.approx(10 * mm)

    def test_equivalent_values_in_different_units_produce_same_page_size(self):
        # 1 inch == 25.4 mm
        pts_via_in, _, _, _ = _resolve_points(1.0, 1.0, "in", 0.2, None, None, None)
        pts_via_mm, _, _, _ = _resolve_points(25.4, 25.4, "mm", 0.2, None, None, None)
        assert pts_via_in == pytest.approx(pts_via_mm)


class TestWithinMargin:
    def test_coord_at_lower_boundary_is_included(self):
        assert _within_margin(5.0, 100.0, 5.0) is True

    def test_coord_at_upper_boundary_is_included(self):
        assert _within_margin(95.0, 100.0, 5.0) is True

    def test_coord_inside_bounds_is_included(self):
        assert _within_margin(50.0, 100.0, 5.0) is True

    def test_coord_below_lower_boundary_is_excluded(self):
        assert _within_margin(4.9, 100.0, 5.0) is False

    def test_coord_beyond_upper_boundary_is_excluded(self):
        assert _within_margin(95.1, 100.0, 5.0) is False


class TestNearestGridCoord:
    def test_target_on_center_snaps_to_center(self):
        assert _nearest_grid_coord(50.0, 50.0, 10.0) == pytest.approx(50.0)

    def test_target_closer_to_upper_grid_snaps_up(self):
        # 56 is between grid points 50 and 60, closer to 60
        assert _nearest_grid_coord(56.0, 50.0, 10.0) == pytest.approx(60.0)

    def test_target_closer_to_lower_grid_snaps_down(self):
        # 54 is between grid points 50 and 60, closer to 50
        assert _nearest_grid_coord(54.0, 50.0, 10.0) == pytest.approx(50.0)

    def test_snaps_in_negative_direction(self):
        assert _nearest_grid_coord(44.0, 50.0, 10.0) == pytest.approx(40.0)


class TestGridDots:
    def test_center_dot_is_always_present(self):
        page, spacing = 100.0, 10.0
        center = page / 2
        dots = _grid_dots(center, center, page, page, spacing, 1.0)
        assert (center, center) in dots

    def test_adjacent_dots_are_exactly_one_spacing_apart(self):
        page, spacing = 100.0, 10.0
        center = page / 2
        dots = _grid_dots(center, center, page, page, spacing, 1.0)
        xs = sorted({dot_x for dot_x, _ in dots})
        gaps = [xs[i + 1] - xs[i] for i in range(len(xs) - 1)]
        assert all(g == pytest.approx(spacing) for g in gaps)

    def test_no_dot_falls_outside_margin(self):
        page, spacing, margin = 100.0, 10.0, 15.0
        center = page / 2
        dots = _grid_dots(center, center, page, page, spacing, margin)
        for dot_x, dot_y in dots:
            assert dot_x >= margin
            assert dot_x <= page - margin
            assert dot_y >= margin
            assert dot_y <= page - margin

    def test_margin_larger_than_page_produces_no_dots(self):
        dots = _grid_dots(50.0, 50.0, 100.0, 100.0, 10.0, 51.0)
        assert len(dots) == 0


class TestCenterCrossDots:
    def test_produces_four_dots_for_a_normal_page(self):
        page, spacing = 100.0, 10.0
        center = page / 2
        dots = _center_cross_dots(center, center, page, page, spacing, 1.0)
        assert len(dots) == 4

    def test_dots_are_at_half_spacing_distance_from_center(self):
        page, spacing = 100.0, 10.0
        center = page / 2
        half = spacing / 2
        dots = _center_cross_dots(center, center, page, page, spacing, 1.0)
        assert (center - half, center) in dots
        assert (center + half, center) in dots
        assert (center, center - half) in dots
        assert (center, center + half) in dots

    def test_dots_outside_margin_are_excluded(self):
        # half_spacing (5) pushes cross dots to x=1 and x=11 — both outside margin=2
        page, spacing, margin = 12.0, 10.0, 2.0
        center = page / 2
        dots = _center_cross_dots(center, center, page, page, spacing, margin)
        assert len(dots) == 0


class TestCornerMarkerDots:
    def test_produces_eight_dots(self):
        # page=120, spacing=10: third divisions land exactly on grid points
        page, spacing = 120.0, 10.0
        center = page / 2
        dots = _corner_marker_dots(center, center, page, page, spacing)
        assert len(dots) == 8

    def test_dots_are_offset_from_third_divisions_by_half_spacing(self):
        page, spacing = 120.0, 10.0
        center = page / 2
        half = spacing / 2
        # nearest_grid(40, 60, 10) = 40; nearest_grid(80, 60, 10) = 80
        dots = _corner_marker_dots(center, center, page, page, spacing)
        # Each corner contributes one horizontal and one vertical offset dot
        assert (40.0 - half, 80.0) in dots  # upper-left, horizontal offset
        assert (40.0, 80.0 + half) in dots  # upper-left, vertical offset


class TestComputeDotPositions:
    def test_result_contains_all_grid_dots(self):
        page, spacing = 100.0, 10.0
        center = page / 2
        grid = _grid_dots(center, center, page, page, spacing, 1.0)
        all_dots = _compute_dot_positions(center, center, page, page, spacing, 1.0)
        assert grid.issubset(all_dots)

    def test_result_contains_all_center_cross_dots(self):
        page, spacing = 100.0, 10.0
        center = page / 2
        cross = _center_cross_dots(center, center, page, page, spacing, 1.0)
        all_dots = _compute_dot_positions(center, center, page, page, spacing, 1.0)
        assert cross.issubset(all_dots)

    def test_result_contains_all_corner_marker_dots(self):
        page, spacing = 120.0, 10.0
        center = page / 2
        corners = _corner_marker_dots(center, center, page, page, spacing)
        all_dots = _compute_dot_positions(center, center, page, page, spacing, 1.0)
        assert corners.issubset(all_dots)


class TestGenerateDotPaper:
    def test_creates_non_empty_pdf_file(self, tmp_path):
        output = tmp_path / "output.pdf"
        generate_dot_paper(output_path=str(output))
        assert output.exists()
        assert output.stat().st_size > 0

    def test_equivalent_units_produce_same_dot_count(self):
        # 6.32 in × 8.17 in == 160.528 mm × 207.518 mm
        spacing_pts = 5 * mm
        margin_pts = spacing_pts

        dots_from_in = _compute_dot_positions(
            6.32 * inch / 2,
            8.17 * inch / 2,
            6.32 * inch,
            8.17 * inch,
            spacing_pts,
            margin_pts,
        )
        dots_from_mm = _compute_dot_positions(
            160.528 * mm / 2,
            207.518 * mm / 2,
            160.528 * mm,
            207.518 * mm,
            spacing_pts,
            margin_pts,
        )
        assert len(dots_from_in) == len(dots_from_mm)

    def test_dot_spacing_unit_override_produces_output(self, tmp_path):
        output = tmp_path / "mixed.pdf"
        generate_dot_paper(
            output_path=str(output),
            page_width=6.32,
            page_height=8.17,
            unit="in",
            dot_spacing=5.0,
            dot_spacing_unit="mm",
        )
        assert output.exists()

    def test_invalid_unit_raises_value_error(self, tmp_path):
        with pytest.raises(ValueError, match="'furlong'"):
            generate_dot_paper(
                output_path=str(tmp_path / "x.pdf"),
                unit="furlong",
            )

    def test_all_supported_units_produce_output(self, tmp_path):
        for unit, width, height in [
            ("in", 6.0, 8.0),
            ("mm", 150.0, 200.0),
            ("cm", 15.0, 20.0),
            ("pt", 432.0, 576.0),
            ("px", 432.0, 576.0),
        ]:
            output = tmp_path / f"output_{unit}.pdf"
            generate_dot_paper(
                output_path=str(output),
                page_width=width,
                page_height=height,
                unit=unit,
            )
            assert output.exists(), f"No output for unit={unit!r}"
