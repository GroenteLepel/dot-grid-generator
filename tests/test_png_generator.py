"""Tests for PNG generation backend."""

import os
import tempfile

import pytest

from dot_paper_generator import png_generator

# Check if PNG rendering is available
try:
    from reportlab.graphics import renderPM

    renderPM._getPMBackend()
    PNG_AVAILABLE = True
except (ImportError, Exception):
    PNG_AVAILABLE = False


@pytest.mark.skipif(
    not PNG_AVAILABLE,
    reason="PNG rendering backend not available (requires rlPyCairo or similar)",
)
class TestGeneratePng:
    """Test PNG generation."""

    def test_png_file_created(self):
        """Test that PNG file is created at specified path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "test.png")
            result = png_generator.generate_png(
                output_path=output_path,
                page_width=8.5,
                page_height=11,
                unit="in",
                dot_spacing=0.2,
                dot_spacing_unit=None,
                bg_color="#FFFFFF",
                dot_color="#000000",
                dot_radius_pt=0.5,
                margin=None,
                margin_unit=None,
                dpi=150,
            )

            assert os.path.exists(output_path)
            assert result == output_path
            assert os.path.getsize(output_path) > 0

    def test_png_is_valid(self):
        """Test that generated PNG file is valid (has PNG header)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "test.png")
            png_generator.generate_png(
                output_path=output_path,
                page_width=8.5,
                page_height=11,
                unit="in",
                dot_spacing=0.2,
                dot_spacing_unit=None,
                bg_color="#FFFFFF",
                dot_color="#000000",
                dot_radius_pt=0.5,
                margin=None,
                margin_unit=None,
                dpi=150,
            )

            with open(output_path, "rb") as f:
                header = f.read(8)
                # PNG file signature
                assert header == b"\x89PNG\r\n\x1a\n"

    @pytest.mark.parametrize("dpi", [72, 150, 300, 600])
    def test_png_with_different_dpi(self, dpi):
        """Test PNG generation at different DPI values."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, f"{dpi}dpi.png")
            result = png_generator.generate_png(
                output_path=output_path,
                page_width=8.5,
                page_height=11,
                unit="in",
                dot_spacing=0.2,
                dot_spacing_unit=None,
                bg_color="#FFFFFF",
                dot_color="#000000",
                dot_radius_pt=0.5,
                margin=None,
                margin_unit=None,
                dpi=dpi,
            )

            assert os.path.exists(output_path)
            assert os.path.getsize(output_path) > 0

    def test_png_with_custom_colors(self):
        """Test PNG generation with custom colors."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "colored.png")
            result = png_generator.generate_png(
                output_path=output_path,
                page_width=8.5,
                page_height=11,
                unit="in",
                dot_spacing=0.2,
                dot_spacing_unit=None,
                bg_color="#F3E4D2",
                dot_color="#929292",
                dot_radius_pt=0.5,
                margin=None,
                margin_unit=None,
                dpi=150,
            )

            assert os.path.exists(output_path)
            assert os.path.getsize(output_path) > 0

    def test_png_with_different_page_sizes(self):
        """Test PNG generation with different page dimensions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Letter (8.5 x 11 inches)
            output_letter = os.path.join(tmpdir, "letter.png")
            png_generator.generate_png(
                output_path=output_letter,
                page_width=8.5,
                page_height=11,
                unit="in",
                dot_spacing=0.2,
                dot_spacing_unit=None,
                bg_color="#FFFFFF",
                dot_color="#000000",
                dot_radius_pt=0.5,
                margin=None,
                margin_unit=None,
                dpi=150,
            )
            assert os.path.exists(output_letter)

            # A4 (210 x 297 mm)
            output_a4 = os.path.join(tmpdir, "a4.png")
            png_generator.generate_png(
                output_path=output_a4,
                page_width=210,
                page_height=297,
                unit="mm",
                dot_spacing=5,
                dot_spacing_unit="mm",
                bg_color="#FFFFFF",
                dot_color="#000000",
                dot_radius_pt=0.5,
                margin=None,
                margin_unit=None,
                dpi=150,
            )
            assert os.path.exists(output_a4)
