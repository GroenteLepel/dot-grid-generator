"""Tests for PDF generation backend."""

import os
import tempfile

import pytest

from dot_paper_generator import pdf_generator


class TestGeneratePdf:
    """Test PDF generation."""

    def test_pdf_file_created(self):
        """Test that PDF file is created at specified path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "test.pdf")
            result = pdf_generator.generate_pdf(
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
            )

            assert os.path.exists(output_path)
            assert result == output_path
            assert os.path.getsize(output_path) > 0

    def test_pdf_is_valid(self):
        """Test that generated PDF file is valid (has PDF header)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "test.pdf")
            pdf_generator.generate_pdf(
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
            )

            with open(output_path, "rb") as f:
                header = f.read(4)
                assert header == b"%PDF"

    def test_pdf_with_custom_colors(self):
        """Test PDF generation with custom colors."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "colored.pdf")
            result = pdf_generator.generate_pdf(
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
            )

            assert os.path.exists(output_path)
            assert os.path.getsize(output_path) > 0

    @pytest.mark.parametrize(
        "name,width,height,unit,spacing",
        [
            ("letter", 8.5, 11, "in", 0.2),
            ("a4", 210, 297, "mm", 5),
            ("a5", 148, 210, "mm", 5),
        ],
    )
    def test_pdf_with_different_page_sizes(self, name, width, height, unit, spacing):
        """Test PDF generation with different page dimensions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, f"{name}.pdf")
            pdf_generator.generate_pdf(
                output_path=output_path,
                page_width=width,
                page_height=height,
                unit=unit,
                dot_spacing=spacing,
                dot_spacing_unit=None,
                bg_color="#FFFFFF",
                dot_color="#000000",
                dot_radius_pt=0.5,
                margin=None,
                margin_unit=None,
            )
            assert os.path.exists(output_path)

    def test_pdf_with_custom_margin(self):
        """Test PDF generation with custom margin."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "margin.pdf")
            pdf_generator.generate_pdf(
                output_path=output_path,
                page_width=8.5,
                page_height=11,
                unit="in",
                dot_spacing=0.2,
                dot_spacing_unit=None,
                bg_color="#FFFFFF",
                dot_color="#000000",
                dot_radius_pt=0.5,
                margin=0.75,
                margin_unit="in",
            )
            assert os.path.exists(output_path)
            assert os.path.getsize(output_path) > 0
