"""PDF rendering backend for dot-grid generator.

Renders dot positions to PDF format using ReportLab canvas.
"""

from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas

from dot_paper_generator._rendering import prepare_rendering


def generate_pdf(
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
    verbose: bool = True,
) -> str:
    """Generate a PDF with a dot-grid pattern.

    Args:
        output_path: File path where PDF will be saved
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
        verbose: Print generation status (default True)

    Returns:
        File path of generated PDF.
    """
    ctx = prepare_rendering(
        page_width,
        page_height,
        unit,
        dot_spacing,
        dot_spacing_unit,
        margin,
        margin_unit,
    )

    pdf = canvas.Canvas(output_path, pagesize=(ctx.page_width_pts, ctx.page_height_pts))
    _draw_background(pdf, ctx.page_width_pts, ctx.page_height_pts, bg_color)
    _draw_dots(pdf, ctx.dots, dot_color, dot_radius_pt)
    pdf.save()

    if verbose:
        print(
            f"Generated: {output_path} ({ctx.page_width}×{ctx.page_height} {ctx.unit}, {ctx.dot_count} dots)"
        )
    return output_path


def _draw_background(
    pdf: canvas.Canvas, page_width_pts: float, page_height_pts: float, bg_color: str
) -> None:
    """Draw solid background color."""
    pdf.setFillColor(HexColor(bg_color))
    pdf.rect(0, 0, page_width_pts, page_height_pts, stroke=0, fill=1)


def _draw_dots(
    pdf: canvas.Canvas,
    dots: set[tuple[float, float]],
    dot_color: str,
    dot_radius_pt: float,
) -> None:
    """Draw all dots on the canvas."""
    pdf.setFillColor(HexColor(dot_color))
    pdf.setStrokeColor(HexColor(dot_color))
    for dot_x, dot_y in dots:
        pdf.circle(dot_x, dot_y, dot_radius_pt, stroke=0, fill=1)
