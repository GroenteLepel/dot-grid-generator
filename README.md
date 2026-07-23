# Dot Paper Generator

Generate dot-grid PDF files for digital note-taking.

## Example Output

<p align="center">
  <img src="docs/images/default_example.png" alt="Default dot grid paper" width="400">
</p>

The generated page features a centered dot grid with a **center cross** (half-spacing dots marking the exact center) and **corner markers** at the 1/3 and 2/3 page divisions:

<p align="center">
  <img src="docs/images/center_cross_detail.png" alt="Center cross detail" width="300">
</p>

## Installation

```bash
git clone https://github.com/daniel-kok/dot-grid-generator.git
cd dot-grid-generator
poetry install
```

## Usage

### Command Line

Generate a dot-grid PDF with default settings:

```bash
poetry run python -m dot_paper_generator.generator
```

This creates a `dot_paper.pdf` in the current directory.

### Python API

```python
from dot_paper_generator.generator import generate_dot_paper

# Generate with default settings
generate_dot_paper()

# Customize the output (dimensions in inches)
generate_dot_paper(
    output_path="my_dot_paper.pdf",
    page_width=8.5,        # US Letter width
    page_height=11.0,      # US Letter height
    unit="in",             # "in", "mm", "cm", "m", "px", "pt"
    dot_spacing=0.2,       # Distance between dots (in unit)
    bg_color="#F3E4D2",   # Background color (hex)
    dot_color="#929292",  # Dot color (hex)
    dot_radius_pt=0.5,    # Dot size in points
    margin=5.0,           # Page margin (in unit)
)

# Mix units: A5 page in mm, spacing in mm
generate_dot_paper(
    page_width=148,
    page_height=210,
    unit="mm",
    dot_spacing=5.0,
)

# Override spacing unit independently
generate_dot_paper(
    page_width=6.32,
    page_height=8.17,
    unit="in",
    dot_spacing=5.0,
    dot_spacing_unit="mm",  # spacing stays in mm regardless of page unit
)
```

### Default Settings

| Parameter          | Default         | Description                                              |
|--------------------|-----------------|----------------------------------------------------------|
| `output_path`      | `dot_paper.pdf` | Output file path                                         |
| `page_width`       | `6.32`          | Page width (in `unit`)                                   |
| `page_height`      | `8.17`          | Page height (in `unit`)                                  |
| `unit`             | `in`            | Unit for page dimensions: `in`, `mm`, `cm`, `m`, `px`, `pt` |
| `dot_spacing`      | `0.2`           | Spacing between dots (in `dot_spacing_unit` or `unit`)   |
| `dot_spacing_unit` | `None`          | Override unit for `dot_spacing` (defaults to `unit`)     |
| `bg_color`         | `#F3E4D2`       | Background color (warm cream)                            |
| `dot_color`        | `#929292`       | Dot color (medium gray)                                  |
| `dot_radius_pt`    | `0.5`           | Dot radius in points                                     |
| `margin`           | `None`          | Page margin (in `margin_unit` or `unit`; defaults to `dot_spacing`) |
| `margin_unit`      | `None`          | Override unit for `margin` (defaults to `unit`)          |

## PNG Output

Generate high-quality PNG files at configurable DPI (default 300 DPI):

```bash
# CLI: Generate 300 DPI PNG with preset
poetry run python -m dot_paper_generator --format png --dpi 300 -o grid.png ipad_goodnotes

# CLI: Generate 150 DPI PNG for screen display
poetry run python -m dot_paper_generator --format png --dpi 150 supernote_nomad
```

### Python API

```python
from dot_paper_generator import generate_dot_paper

# Generate PNG at 300 DPI (high-quality print)
generate_dot_paper(
    output_format="png",
    output_path="grid.png",
    dpi=300,
    page_width=8.5,
    page_height=11,
    unit="in",
)

# Generate 150 DPI PNG with custom preset
generate_dot_paper(
    output_format="png",
    dpi=150,
    **load_preset("ipad_goodnotes")
)
```

### DPI Options

| DPI | Use Case |
|-----|----------|
| 72 | Screen display only |
| 150 | Balanced quality/size |
| 300 | High-quality print (default) |
| 600 | Very high-quality print (large file) |

**Note:** PNG rendering requires optional ReportLab dependencies. On macOS/Linux, install with:
```bash
pip install 'reportlab[rlPyCairo]'
```
If dependencies aren't available, PNG generation will raise an informative error and PDF output remains fully functional.

