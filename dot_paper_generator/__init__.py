"""Dot Grid Generator - Create customizable dot-grid PDFs and PNGs for digital note-taking devices.

Example usage:
    from dot_paper_generator import generate_dot_paper, load_preset

    # Generate PDF with preset
    generate_dot_paper(output_format="pdf", **load_preset("ipad_goodnotes"))

    # Generate high-quality PNG at 300 DPI
    generate_dot_paper(
        output_format="png",
        output_path="grid.png",
        dpi=300,
        **load_preset("supernote_nomad")
    )

    # Generate with custom parameters
    generate_dot_paper(
        output_format="pdf",
        page_width=8.5,
        page_height=11,
        unit="in",
        dot_spacing=0.2,
        bg_color="#FFFFFF",
        dot_color="#000000",
    )
"""

from dot_paper_generator.generator import generate_dot_paper
from dot_paper_generator.presets import load_preset

__all__ = ["generate_dot_paper", "load_preset"]
