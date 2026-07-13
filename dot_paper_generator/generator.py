from reportlab.lib.colors import HexColor
from reportlab.lib.units import cm, inch, mm
from reportlab.pdfgen import canvas

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


def _to_points(value: float, unit: str) -> float:
    """Convert a dimension from *unit* to ReportLab points."""
    factor = _UNIT_TO_POINTS.get(unit.lower())
    if factor is None:
        valid = ", ".join(sorted(_UNIT_TO_POINTS))
        raise ValueError(f"Unknown unit {unit!r}. Valid options: {valid}")
    return value * factor


def _resolve_points(
    page_width: float,
    page_height: float,
    unit: str,
    dot_spacing: float,
    dot_spacing_unit: str | None,
    margin: float | None,
    margin_unit: str | None,
) -> tuple[float, float, float, float]:
    """Convert all user-supplied dimensions to ReportLab points.

    Returns (page_w, page_h, spacing, margin_pts).
    """
    spacing_unit = dot_spacing_unit or unit
    page_w = _to_points(page_width, unit)
    page_h = _to_points(page_height, unit)
    spacing = _to_points(dot_spacing, spacing_unit)
    margin_pts = spacing if margin is None else _to_points(margin, margin_unit or unit)
    return page_w, page_h, spacing, margin_pts


def _within_margin(coord: float, limit: float, margin: float) -> bool:
    return margin <= coord <= limit - margin


def _draw_background(
    c: canvas.Canvas, page_w: float, page_h: float, bg_color: str
) -> None:
    c.setFillColor(HexColor(bg_color))
    c.rect(0, 0, page_w, page_h, stroke=0, fill=1)


def _nearest_grid_coord(target: float, center: float, spacing: float) -> float:
    return center + round((target - center) / spacing) * spacing


def _grid_dots(
    cx: float,
    cy: float,
    page_w: float,
    page_h: float,
    spacing: float,
    margin_pts: float,
) -> set[tuple[float, float]]:
    dots: set[tuple[float, float]] = set()
    cols_half = int(cx // spacing)
    rows_half = int(cy // spacing)
    for col in range(-cols_half, cols_half + 1):
        for row in range(-rows_half, rows_half + 1):
            x = cx + col * spacing
            y = cy + row * spacing
            if _within_margin(x, page_w, margin_pts) and _within_margin(
                y, page_h, margin_pts
            ):
                dots.add((x, y))
    return dots


def _center_cross_dots(
    cx: float,
    cy: float,
    page_w: float,
    page_h: float,
    spacing: float,
    margin_pts: float,
) -> set[tuple[float, float]]:
    """Half-spacing dots along both axes marking the exact page centre."""
    dots: set[tuple[float, float]] = set()
    half = spacing / 2
    for direction in (-1, 1):
        cross_x = cx + direction * half
        if _within_margin(cross_x, page_w, margin_pts):
            dots.add((cross_x, cy))
        cross_y = cy + direction * half
        if _within_margin(cross_y, page_h, margin_pts):
            dots.add((cx, cross_y))
    return dots


def _corner_marker_dots(
    cx: float,
    cy: float,
    page_w: float,
    page_h: float,
    spacing: float,
) -> set[tuple[float, float]]:
    """Half-spacing dots at the 1/3 and 2/3 grid divisions (3×3 corner markers)."""
    dots: set[tuple[float, float]] = set()
    half = spacing / 2
    third_x = _nearest_grid_coord(page_w / 3, cx, spacing)
    twothird_x = _nearest_grid_coord(2 * page_w / 3, cx, spacing)
    third_y = _nearest_grid_coord(page_h / 3, cy, spacing)
    twothird_y = _nearest_grid_coord(2 * page_h / 3, cy, spacing)
    # (grid_x, grid_y, dx_direction, dy_direction) — directions toward outside
    corners = [
        (third_x, twothird_y, -1, +1),  # upper-left:  left & up
        (twothird_x, twothird_y, +1, +1),  # upper-right: right & up
        (third_x, third_y, -1, -1),  # lower-left:  left & down
        (twothird_x, third_y, +1, -1),  # lower-right: right & down
    ]
    for gx, gy, dx, dy in corners:
        dots.add((gx + dx * half, gy))
        dots.add((gx, gy + dy * half))
    return dots


def _compute_dot_positions(
    cx: float,
    cy: float,
    page_w: float,
    page_h: float,
    spacing: float,
    margin_pts: float,
) -> set[tuple[float, float]]:
    dots = _grid_dots(cx, cy, page_w, page_h, spacing, margin_pts)
    dots |= _center_cross_dots(cx, cy, page_w, page_h, spacing, margin_pts)
    dots |= _corner_marker_dots(cx, cy, page_w, page_h, spacing)
    return dots


def _draw_dots(
    c: canvas.Canvas,
    dots: set[tuple[float, float]],
    dot_color: str,
    dot_radius_pt: float,
) -> None:
    c.setFillColor(HexColor(dot_color))
    c.setStrokeColor(HexColor(dot_color))
    for x, y in dots:
        c.circle(x, y, dot_radius_pt, stroke=0, fill=1)


def generate_dot_paper(
    output_path: str = "dot_paper.pdf",
    page_width: float = 6.32,
    page_height: float = 8.17,
    unit: str = "in",
    dot_spacing: float = 0.2,
    dot_spacing_unit: str | None = None,
    bg_color: str = "#F3E4D2",
    dot_color: str = "#929292",
    dot_radius_pt: float = 0.5,
    margin: float | None = None,
    margin_unit: str | None = None,
) -> None:
    """Generate a dot-grid PDF with a centered grid and center cross."""
    page_w, page_h, spacing, margin_pts = _resolve_points(
        page_width,
        page_height,
        unit,
        dot_spacing,
        dot_spacing_unit,
        margin,
        margin_unit,
    )
    cx, cy = page_w / 2, page_h / 2

    c = canvas.Canvas(output_path, pagesize=(page_w, page_h))
    _draw_background(c, page_w, page_h, bg_color)

    dots = _compute_dot_positions(cx, cy, page_w, page_h, spacing, margin_pts)
    _draw_dots(c, dots, dot_color, dot_radius_pt)

    c.save()
    print(
        f"Generated: {output_path} ({page_width}×{page_height} {unit}, {len(dots)} dots)"
    )


def main() -> None:
    generate_dot_paper(
        page_width=6.32,
        page_height=7.6,
    )


if __name__ == "__main__":
    main()
