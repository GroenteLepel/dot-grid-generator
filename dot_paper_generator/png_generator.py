"""PNG rendering backend for dot-grid generator.

Renders dot positions to PNG format using ReportLab renderPM.

Note: PNG rendering requires optional ReportLab dependencies (rlPyCairo or _rl_renderPM).
Install with: pip install reportlab[rlPyCairo] or similar.
"""

from reportlab.graphics import renderPM
from reportlab.graphics.shapes import Drawing, Circle, Rect
from reportlab.lib.colors import HexColor

from dot_paper_generator._rendering import prepare_rendering, RenderingContext


def generate_png(
    output_path: str,
    page_width: float,
    page_height: float,
    unit: str,
    dot_spacing: float,
    dot_spacing_unit: str | None,
    bg_color: str,
    dot_color: str,
    dot_radius_pt: float,
    margin: float | None,
    margin_unit: str | None,
    dpi: int = 300,
    verbose: bool = True,
) -> str:
    """Generate a PNG with a dot-grid pattern.

    Args:
        output_path: File path where PNG will be saved
        page_width: Page width in specified units
        page_height: Page height in specified units
        unit: Unit for page dimensions ("in", "mm", "cm", etc.)
        dot_spacing: Spacing between dots in specified units
        dot_spacing_unit: Unit for dot spacing (defaults to page unit)
        bg_color: Background color as hex string (e.g., "#FFFFFF")
        dot_color: Dot color as hex string (e.g., "#000000")
        dot_radius_pt: Dot radius in points
        margin: Margin from edges (defaults to dot_spacing)
        margin_unit: Unit for margin (defaults to page unit)
        dpi: Dots per inch for PNG rendering (default 300 for high quality)
        verbose: Print generation status (default True)

    Returns:
        File path of generated PNG.

    Raises:
        ImportError: If PNG rendering backend (rlPyCairo or _rl_renderPM) is not available.
    """
    _verify_renderpm_available()

    ctx = prepare_rendering(
        page_width,
        page_height,
        unit,
        dot_spacing,
        dot_spacing_unit,
        margin,
        margin_unit,
    )

    drawing = _create_drawing_with_dots(ctx, bg_color, dot_color, dot_radius_pt)
    _render_drawing_to_file(drawing, output_path, dpi)

    if verbose:
        print(
            f"Generated: {output_path} ({ctx.page_width}×{ctx.page_height} {ctx.unit} @ {dpi} dpi, {ctx.dot_count} dots)"
        )
    return output_path


def _verify_renderpm_available() -> None:
    """Verify that PNG rendering backend is available.

    Raises:
        ImportError: If renderPM backend (rlPyCairo or _rl_renderPM) is not installed.
    """
    try:
        renderPM._getPMBackend()
    except (ImportError, Exception) as e:
        raise ImportError(
            "PNG rendering requires optional ReportLab dependencies. "
            "Install with: pip install 'reportlab[rlPyCairo]' or ensure "
            "development tools and cairo libraries are installed."
        ) from e


def _create_drawing_with_dots(
    ctx: RenderingContext,
    bg_color: str,
    dot_color: str,
    dot_radius_pt: float,
) -> Drawing:
    """Create a Drawing object populated with background and dots."""
    drawing = Drawing(ctx.page_width_pts, ctx.page_height_pts)
    _add_background_to_drawing(
        drawing, ctx.page_width_pts, ctx.page_height_pts, bg_color
    )
    _add_dots_to_drawing(drawing, ctx.dots, dot_color, dot_radius_pt)
    return drawing


def _add_background_to_drawing(
    drawing: Drawing, page_width_pts: float, page_height_pts: float, bg_color: str
) -> None:
    """Add solid background rectangle to the drawing."""
    bg_rect = Rect(0, 0, page_width_pts, page_height_pts, fillColor=HexColor(bg_color))
    drawing.add(bg_rect)


def _add_dots_to_drawing(
    drawing: Drawing,
    dots: set[tuple[float, float]],
    dot_color: str,
    dot_radius_pt: float,
) -> None:
    """Add all dot circles to the drawing."""
    dot_color_obj = HexColor(dot_color)
    for dot_x, dot_y in dots:
        dot = Circle(dot_x, dot_y, dot_radius_pt, fillColor=dot_color_obj)
        drawing.add(dot)


def _render_drawing_to_file(drawing: Drawing, output_path: str, dpi: int) -> None:
    """Render drawing to PNG file at specified DPI."""
    renderPM.drawToFile(drawing, output_path, fmt="PNG", dpi=dpi)
