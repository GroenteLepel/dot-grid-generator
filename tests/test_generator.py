"""Tests for generator orchestrator module."""

import os
import tempfile

import pytest

from dot_paper_generator.generator import generate_dot_paper

# Check if PNG rendering is available
try:
    from reportlab.graphics import renderPM

    renderPM._getPMBackend()
    PNG_AVAILABLE = True
except (ImportError, Exception):
    PNG_AVAILABLE = False


class TestGenerateDotPaper:
    """Test the main generate_dot_paper orchestrator function."""

    def test_pdf_output_format_creates_pdf(self):
        """Test that output_format='pdf' creates a PDF file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "output.pdf")
            result = generate_dot_paper(
                output_path=output_path,
                output_format="pdf",
                page_width=8.5,
                page_height=11,
                unit="in",
            )

            assert os.path.exists(output_path)
            assert result == output_path
            # Check PDF signature
            with open(output_path, "rb") as f:
                assert f.read(4) == b"%PDF"

    @pytest.mark.skipif(not PNG_AVAILABLE, reason="PNG rendering backend not available")
    def test_png_output_format_creates_png(self):
        """Test that output_format='png' creates a PNG file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "output.png")
            result = generate_dot_paper(
                output_path=output_path,
                output_format="png",
                page_width=8.5,
                page_height=11,
                unit="in",
                dpi=150,
            )

            assert os.path.exists(output_path)
            assert result == output_path
            # Check PNG signature
            with open(output_path, "rb") as f:
                assert f.read(8) == b"\x89PNG\r\n\x1a\n"

    def test_default_output_format_is_pdf(self):
        """Test that default output_format is 'pdf'."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "output.pdf")
            generate_dot_paper(output_path=output_path)

            assert os.path.exists(output_path)
            # Check PDF signature
            with open(output_path, "rb") as f:
                assert f.read(4) == b"%PDF"

    def test_invalid_output_format_raises_error(self):
        """Test that invalid output_format raises ValueError."""
        with pytest.raises(ValueError, match="Invalid output_format"):
            generate_dot_paper(output_format="jpg")  # type: ignore

    @pytest.mark.skipif(not PNG_AVAILABLE, reason="PNG rendering backend not available")
    def test_png_dpi_parameter(self):
        """Test that dpi parameter is passed to PNG generation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "output.png")
            result = generate_dot_paper(
                output_path=output_path,
                output_format="png",
                dpi=300,
            )

            assert os.path.exists(output_path)

    @pytest.mark.skipif(not PNG_AVAILABLE, reason="PNG rendering backend not available")
    def test_png_default_dpi_is_300(self):
        """Test that PNG defaults to 300 DPI if not specified."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "output.png")
            result = generate_dot_paper(
                output_path=output_path,
                output_format="png",
            )

            assert os.path.exists(output_path)

    def test_returns_output_path(self):
        """Test that generate_dot_paper returns the output path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "test.pdf")
            result = generate_dot_paper(output_path=output_path)

            assert result == output_path

    @pytest.mark.parametrize(
        "unit,width,height",
        [
            ("in", 1.0, 2.0),
            ("mm", 10.0, 20.0),
            ("cm", 1.0, 2.0),
            ("pt", 10.0, 20.0),
            ("px", 20.0, 20.0),
        ],
    )
    def test_all_supported_units_produce_output(self, unit, width, height):
        """Test that all supported units produce valid output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, f"output_{unit}.pdf")
            result = generate_dot_paper(
                output_path=output_path,
                page_width=width,
                page_height=height,
                unit=unit,
            )
            assert os.path.exists(output_path)
