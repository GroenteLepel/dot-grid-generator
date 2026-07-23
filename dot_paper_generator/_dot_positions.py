"""Private module for dot position calculations.

This module contains pure computation logic for calculating dot grid positions.
It's used by both PDF and PNG rendering backends to ensure dot positions
are identical across output formats.
"""

from reportlab.lib.units import cm, inch, mm


def compute_dot_positions(
    center_x: float,
    center_y: float,
    page_width_pts: float,
    page_height_pts: float,
    spacing: float,
    margin_pts: float,
) -> set[tuple[float, float]]:
    """Compute all dot positions for a grid.

    Returns a set of (x, y) tuples representing dot positions in points.
    Includes regular grid, center cross, and corner markers.
    """
    dots = grid_dots(
        center_x, center_y, page_width_pts, page_height_pts, spacing, margin_pts
    )
    dots |= center_cross_dots(
        center_x, center_y, page_width_pts, page_height_pts, spacing, margin_pts
    )
    dots |= corner_marker_dots(
        center_x, center_y, page_width_pts, page_height_pts, spacing
    )
    return dots


def grid_dots(
    center_x: float,
    center_y: float,
    page_width_pts: float,
    page_height_pts: float,
    spacing: float,
    margin_pts: float,
) -> set[tuple[float, float]]:
    """Generate regular grid dots centered on the page."""
    dots: set[tuple[float, float]] = set()
    cols_half = int(center_x // spacing)
    rows_half = int(center_y // spacing)
    for col in range(-cols_half, cols_half + 1):
        for row in range(-rows_half, rows_half + 1):
            dot_x = center_x + col * spacing
            dot_y = center_y + row * spacing
            if _within_margin(dot_x, page_width_pts, margin_pts) and _within_margin(
                dot_y, page_height_pts, margin_pts
            ):
                dots.add((dot_x, dot_y))
    return dots


def center_cross_dots(
    center_x: float,
    center_y: float,
    page_width_pts: float,
    page_height_pts: float,
    spacing: float,
    margin_pts: float,
) -> set[tuple[float, float]]:
    """Half-spacing dots along both axes marking the exact page centre."""
    dots: set[tuple[float, float]] = set()
    half_spacing = spacing / 2
    for direction in (-1, 1):
        cross_x = center_x + direction * half_spacing
        if _within_margin(cross_x, page_width_pts, margin_pts):
            dots.add((cross_x, center_y))
        cross_y = center_y + direction * half_spacing
        if _within_margin(cross_y, page_height_pts, margin_pts):
            dots.add((center_x, cross_y))
    return dots


def corner_marker_dots(
    center_x: float,
    center_y: float,
    page_width_pts: float,
    page_height_pts: float,
    spacing: float,
) -> set[tuple[float, float]]:
    """Half-spacing dots at the 1/3 and 2/3 grid divisions (3×3 corner markers)."""
    dots: set[tuple[float, float]] = set()
    half_spacing = spacing / 2
    third_x = _nearest_grid_coord(page_width_pts / 3, center_x, spacing)
    twothird_x = _nearest_grid_coord(2 * page_width_pts / 3, center_x, spacing)
    third_y = _nearest_grid_coord(page_height_pts / 3, center_y, spacing)
    twothird_y = _nearest_grid_coord(2 * page_height_pts / 3, center_y, spacing)
    # (grid_x, grid_y, direction_x, direction_y) — directions toward outside
    corners = [
        (third_x, twothird_y, -1, +1),  # upper-left:  left & up
        (twothird_x, twothird_y, +1, +1),  # upper-right: right & up
        (third_x, third_y, -1, -1),  # lower-left:  left & down
        (twothird_x, third_y, +1, -1),  # lower-right: right & down
    ]
    for grid_x, grid_y, direction_x, direction_y in corners:
        dots.add((grid_x + direction_x * half_spacing, grid_y))
        dots.add((grid_x, grid_y + direction_y * half_spacing))
    return dots


def resolve_points(
    page_width: float,
    page_height: float,
    unit: str,
    dot_spacing: float,
    dot_spacing_unit: str | None,
    margin: float | None,
    margin_unit: str | None,
) -> tuple[float, float, float, float]:
    """Convert all user-supplied dimensions to ReportLab points.

    Returns (page_width_pts, page_height_pts, spacing, margin_pts).
    """
    spacing_unit = dot_spacing_unit or unit
    page_width_pts = to_points(page_width, unit)
    page_height_pts = to_points(page_height, unit)
    spacing = to_points(dot_spacing, spacing_unit)
    margin_pts = spacing if margin is None else to_points(margin, margin_unit or unit)
    return page_width_pts, page_height_pts, spacing, margin_pts


def to_points(value: float, unit: str) -> float:
    """Convert a dimension from *unit* to ReportLab points."""
    factor = _UNIT_TO_POINTS.get(unit.lower())
    if factor is None:
        valid = ", ".join(sorted(_UNIT_TO_POINTS))
        raise ValueError(f"Unknown unit {unit!r}. Valid options: {valid}")
    return value * factor


def _within_margin(coord: float, limit: float, margin: float) -> bool:
    return margin <= coord <= limit - margin


def _nearest_grid_coord(target: float, center: float, spacing: float) -> float:
    return center + round((target - center) / spacing) * spacing


_UNIT_TO_POINTS: dict[str, float] = {
    "in": inch,
    "inch": inch,
    "inches": inch,
    "mm": mm,
    "cm": cm,
    "m": cm * 100,
    "px": 1.0,  # PDF standard: 1 px = 1 pt at 72 dpi
    "pt": 1.0,
    "point": 1.0,
    "points": 1.0,
}
