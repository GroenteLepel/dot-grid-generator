"""Shared rendering context and utilities.

Provides common setup for both PDF and PNG rendering backends.
"""

from dataclasses import dataclass

from dot_paper_generator._dot_positions import compute_dot_positions, resolve_points


@dataclass
class RenderingContext:
    """Resolved parameters and computed dots for rendering."""

    page_width_pts: float
    page_height_pts: float
    spacing: float
    margin_pts: float
    center_x: float
    center_y: float
    dots: set[tuple[float, float]]
    page_width: float
    page_height: float
    unit: str
    dot_count: int


def prepare_rendering(
    page_width: float,
    page_height: float,
    unit: str,
    dot_spacing: float,
    dot_spacing_unit: str | None,
    margin: float | None,
    margin_unit: str | None,
) -> RenderingContext:
    """Prepare common rendering parameters and compute dot positions.

    Args:
        page_width: Page width in specified units
        page_height: Page height in specified units
        unit: Unit for page dimensions
        dot_spacing: Spacing between dots
        dot_spacing_unit: Unit for dot spacing (defaults to unit)
        margin: Margin from edges (defaults to dot_spacing)
        margin_unit: Unit for margin (defaults to unit)

    Returns:
        RenderingContext with all resolved parameters and computed dots.
    """
    page_width_pts, page_height_pts, spacing, margin_pts = resolve_points(
        page_width,
        page_height,
        unit,
        dot_spacing,
        dot_spacing_unit,
        margin,
        margin_unit,
    )
    center_x, center_y = _calculate_page_center(page_width_pts, page_height_pts)

    dots = compute_dot_positions(
        center_x, center_y, page_width_pts, page_height_pts, spacing, margin_pts
    )

    return RenderingContext(
        page_width_pts=page_width_pts,
        page_height_pts=page_height_pts,
        spacing=spacing,
        margin_pts=margin_pts,
        center_x=center_x,
        center_y=center_y,
        dots=dots,
        page_width=page_width,
        page_height=page_height,
        unit=unit,
        dot_count=len(dots),
    )


def _calculate_page_center(
    page_width_pts: float, page_height_pts: float
) -> tuple[float, float]:
    """Calculate the center point of the page."""
    return page_width_pts / 2, page_height_pts / 2
