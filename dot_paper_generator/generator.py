from reportlab.lib.colors import HexColor
from reportlab.lib.units import inch, mm
from reportlab.pdfgen import canvas


def generate_dot_paper(
    output_path: str = "dot_paper.pdf",
    page_width_inches: float = 6.32,
    page_height_inches: float = 8.17,
    dot_spacing_mm: float = 5.0,
    bg_color: str = "#F3E4D2",
    dot_color: str = "#929292",
    dot_radius_pt: float = 0.5,
    margin_mm: float | None = None,
) -> None:
    """Generate a dot-grid PDF with a centered grid and center cross."""
    page_w = page_width_inches * inch
    page_h = page_height_inches * inch
    spacing = dot_spacing_mm * mm
    margin = (dot_spacing_mm if margin_mm is None else margin_mm) * mm

    cx = page_w / 2
    cy = page_h / 2

    c = canvas.Canvas(output_path, pagesize=(page_w, page_h))

    # Draw background
    c.setFillColor(HexColor(bg_color))
    c.rect(0, 0, page_w, page_h, stroke=0, fill=1)

    # Collect dot positions — start from center and expand outward
    dots: set[tuple[float, float]] = set()

    # Calculate how many dots fit in each direction from center
    cols_half = int(cx // spacing)
    rows_half = int(cy // spacing)

    for col in range(-cols_half, cols_half + 1):
        for row in range(-rows_half, rows_half + 1):
            x = cx + col * spacing
            y = cy + row * spacing
            if margin <= x <= page_w - margin and margin <= y <= page_h - margin:
                dots.add((x, y))

    # Center cross: halved spacing along the axes, extending 1 grid unit
    half = spacing / 2
    for direction in (-1, 1):
        # Horizontal axis (y = cy)
        cross_x = cx + direction * half
        if margin <= cross_x <= page_w - margin:
            dots.add((cross_x, cy))
        # Vertical axis (x = cx)
        cross_y = cy + direction * half
        if margin <= cross_y <= page_h - margin:
            dots.add((cx, cross_y))

    # Corner markers: 4 points dividing the page into a 3×3 grid.
    # Snap each 1/3 and 2/3 position to the nearest grid dot, then add
    # half-spacing dots pointing toward the nearest edges only.
    def nearest_grid(target: float, center: float) -> float:
        offset = target - center
        n = round(offset / spacing)
        return center + n * spacing

    third_x = nearest_grid(page_w / 3, cx)
    twothird_x = nearest_grid(2 * page_w / 3, cx)
    third_y = nearest_grid(page_h / 3, cy)
    twothird_y = nearest_grid(2 * page_h / 3, cy)

    # (grid_x, grid_y, dx_direction, dy_direction) — directions toward outside
    corners = [
        (third_x, twothird_y, -1, +1),    # upper-left: left & up
        (twothird_x, twothird_y, +1, +1),  # upper-right: right & up
        (third_x, third_y, -1, -1),        # lower-left: left & down
        (twothird_x, third_y, +1, -1),     # lower-right: right & down
    ]
    for gx, gy, dx, dy in corners:
        dots.add((gx + dx * half, gy))
        dots.add((gx, gy + dy * half))

    # Draw all dots
    c.setFillColor(HexColor(dot_color))
    c.setStrokeColor(HexColor(dot_color))
    for x, y in dots:
        c.circle(x, y, dot_radius_pt, stroke=0, fill=1)

    c.save()
    print(f"Generated: {output_path} ({page_width_inches}×{page_height_inches} in, {len(dots)} dots)")


def main() -> None:
    generate_dot_paper()


if __name__ == "__main__":
    main()
