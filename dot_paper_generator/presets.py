"""Preset configuration management for dot-grid generator."""

from pathlib import Path

import yaml

_PRESETS_DIR = Path(__file__).parent / "presets"


def load_preset(name_or_path: str) -> dict:
    """Load a preset configuration as kwargs for generate_dot_paper().

    Pass a built-in preset name (e.g. ``"ipad_goodnotes"``) to load a
    bundled YAML, or a file path string (with a ``.yaml`` extension) to
    load a custom file.

    The returned dict can be spread directly into ``generate_dot_paper``.
    Explicit kwargs at the call site override preset values::

        # use a preset as-is
        generate_dot_paper(output_path="out.pdf", **load_preset("ipad_goodnotes"))

        # override one value from the preset
        generate_dot_paper(output_path="out.pdf", **{**load_preset("ipad_goodnotes"), "bg_color": "#FFFFFF"})
    """
    path = Path(name_or_path)
    if not path.suffix:
        path = _PRESETS_DIR / f"{name_or_path}.yaml"
    if not path.exists():
        available = ", ".join(p.stem for p in sorted(_PRESETS_DIR.glob("*.yaml")))
        raise FileNotFoundError(
            f"Preset {name_or_path!r} not found. "
            f"Available built-in presets: {available}"
        )
    with path.open() as f:
        return yaml.safe_load(f)
