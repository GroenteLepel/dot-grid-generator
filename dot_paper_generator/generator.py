"""Main orchestrator for dot-grid generation.

Routes to PDF or PNG backends based on output_format parameter.
Provides CLI interface for command-line usage.
"""

import argparse
from typing import Literal

from dot_paper_generator.presets import load_preset
from dot_paper_generator import pdf_generator, png_generator


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Generate customizable dot-grid PDFs and PNGs"
    )
    parser.add_argument(
        "preset",
        nargs="?",
        default="supernote_nomad",
        help="Preset name or path to YAML file (default: supernote_nomad)",
    )
    parser.add_argument(
        "-o",
        "--output",
        dest="output_path",
        default=None,
        help="Output file path (default: dot_paper.pdf or dot_paper.png)",
    )
    parser.add_argument(
        "--format",
        choices=["pdf", "png"],
        default="pdf",
        help="Output format (default: pdf)",
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=300,
        help="DPI for PNG output (default: 300, ignored for PDF)",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Suppress generation output message",
    )

    args = parser.parse_args()

    preset = load_preset(args.preset)
    output_path = _resolve_output_path(args.output_path, args.format)

    generate_dot_paper(
        output_format=args.format,
        output_path=output_path,
        dpi=args.dpi if args.format == "png" else None,
        verbose=not args.quiet,
        **preset,
    )


def generate_dot_paper(
    output_path: str = "dot_paper.pdf",
    output_format: Literal["pdf", "png"] = "pdf",
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
    dpi: int | None = None,
    verbose: bool = True,
) -> str:
    """Generate a dot-grid PDF or PNG with centered grid and center cross.

    Args:
        output_path: File path where output will be saved
        output_format: Output format ("pdf" or "png", default: "pdf")
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
        dpi: Dots per inch for PNG rendering (default 300, ignored for PDF)
        verbose: Print generation status (default True)

    Returns:
        File path of generated output file.

    Raises:
        ValueError: If output_format is not "pdf" or "png"
    """
    if output_format not in ("pdf", "png"):
        raise ValueError(
            f"Invalid output_format: {output_format!r}. Must be 'pdf' or 'png'."
        )

    dpi = _ensure_dpi_for_png(output_format, dpi)
    backend_params = _prepare_backend_parameters(
        output_path,
        page_width,
        page_height,
        unit,
        dot_spacing,
        dot_spacing_unit,
        bg_color,
        dot_color,
        dot_radius_pt,
        margin,
        margin_unit,
        verbose,
    )

    return _route_to_backend(output_format, backend_params, dpi)


def _resolve_output_path(provided_path: str | None, output_format: str) -> str:
    """Resolve output file path, using format-appropriate default if not provided."""
    if provided_path is not None:
        return provided_path
    return "dot_paper.png" if output_format == "png" else "dot_paper.pdf"


def _ensure_dpi_for_png(output_format: str, dpi: int | None) -> int | None:
    """Ensure PNG format has a DPI value (defaults to 300 if not specified)."""
    if output_format == "png" and dpi is None:
        return 300
    return dpi


def _prepare_backend_parameters(
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
    verbose: bool,
) -> dict[str, float | int | str | bool | None]:
    """Prepare parameters common to all rendering backends."""
    return {
        "output_path": output_path,
        "page_width": page_width,
        "page_height": page_height,
        "unit": unit,
        "dot_spacing": dot_spacing,
        "dot_spacing_unit": dot_spacing_unit,
        "bg_color": bg_color,
        "dot_color": dot_color,
        "dot_radius_pt": dot_radius_pt,
        "margin": margin,
        "margin_unit": margin_unit,
        "verbose": verbose,
    }


def _route_to_backend(output_format: str, backend_params: dict, dpi: int | None) -> str:
    """Route parameters to appropriate PDF or PNG rendering backend."""
    if output_format == "pdf":
        return pdf_generator.generate_pdf(**backend_params)
    else:  # png
        return png_generator.generate_png(**backend_params, dpi=dpi)


if __name__ == "__main__":
    main()
