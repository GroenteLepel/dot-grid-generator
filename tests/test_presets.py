from pathlib import Path

import pytest

from dot_paper_generator import generate_dot_paper, load_preset


class TestLoadPreset:
    def test_ipad_goodnotes_loads_successfully(self):
        preset = load_preset("ipad_goodnotes")
        assert isinstance(preset, dict)

    def test_ipad_goodnotes_has_expected_values(self):
        preset = load_preset("ipad_goodnotes")
        assert preset["page_width"] == pytest.approx(6.32)
        assert preset["page_height"] == pytest.approx(7.6)
        assert preset["unit"] == "in"
        assert preset["bg_color"] == "#F3E4D2"
        assert preset["dot_color"] == "#929292"
        assert preset["dot_radius_pt"] == pytest.approx(0.5)

    def test_supernote_nomad_loads_successfully(self):
        preset = load_preset("supernote_nomad")
        assert isinstance(preset, dict)

    def test_supernote_nomad_has_expected_values(self):
        preset = load_preset("supernote_nomad")
        assert preset["page_width"] == 1404
        assert preset["page_height"] == 1872
        assert preset["unit"] == "px"
        assert preset["bg_color"] == "#FFFFFF"
        assert preset["dot_color"] == "#929292"

    def test_unknown_name_raises_file_not_found(self):
        with pytest.raises(FileNotFoundError, match="'nonexistent'"):
            load_preset("nonexistent")

    def test_error_message_lists_available_presets(self):
        with pytest.raises(FileNotFoundError, match="ipad_goodnotes"):
            load_preset("nonexistent")

    def test_explicit_file_path_loads_custom_yaml(self, tmp_path):
        custom = tmp_path / "my_device.yaml"
        custom.write_text(
            "page_width: 5.0\npage_height: 7.0\nunit: in\n"
            "dot_spacing: 0.2\nbg_color: '#FFFFFF'\ndot_color: '#000000'\ndot_radius_pt: 0.5\n"
        )
        preset = load_preset(str(custom))
        assert preset["page_width"] == pytest.approx(5.0)
        assert preset["bg_color"] == "#FFFFFF"

    def test_preset_spreads_into_generate_dot_paper(self, tmp_path):
        output = tmp_path / "ipad.pdf"
        generate_dot_paper(output_path=str(output), **load_preset("ipad_goodnotes"))
        assert output.exists()
        assert output.stat().st_size > 0

    def test_supernote_preset_spreads_into_generate_dot_paper(self, tmp_path):
        output = tmp_path / "supernote.pdf"
        generate_dot_paper(output_path=str(output), **load_preset("supernote_nomad"))
        assert output.exists()
        assert output.stat().st_size > 0

    def test_explicit_kwarg_overrides_preset_value(self, tmp_path):
        output = tmp_path / "override.pdf"
        preset = load_preset("ipad_goodnotes")
        # Override bg_color to white while keeping all other iPad settings
        generate_dot_paper(output_path=str(output), **{**preset, "bg_color": "#FFFFFF"})
        assert output.exists()

    def test_output_path_not_stored_in_preset(self):
        preset = load_preset("ipad_goodnotes")
        assert "output_path" not in preset
