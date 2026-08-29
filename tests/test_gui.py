from pathlib import Path

import pytest
from PySide6.QtWidgets import QApplication

from mpctk.gui.window import MainWindow
from mpctk.music import (
    LAYOUT_CHROMATIC_KEYBOARD,
    LAYOUT_SCALE_PADS,
)


@pytest.fixture(scope="module")
def qt_app():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_gui_defaults_to_scale_pad_generation(qt_app):
    window = MainWindow()

    spec = window._build_spec()

    assert spec.source_root == "C"
    assert spec.target_root == "C"
    assert spec.layout == LAYOUT_SCALE_PADS
    assert spec.scale == "major"
    assert spec.pads == 16
    assert spec.start_octave == 0
    assert window.scale_combo.isEnabled() is True


def test_chromatic_layout_disables_scale(qt_app):
    window = MainWindow()

    window.layout_combo.setCurrentText("Chromatic Keyboard")

    spec = window._build_spec()

    assert spec.layout == LAYOUT_CHROMATIC_KEYBOARD
    assert spec.scale is None
    assert window.scale_combo.isEnabled() is False


def test_generate_button_uses_existing_generation_pipeline(
    qt_app,
    monkeypatch,
    tmp_path,
):
    window = MainWindow()

    wav = tmp_path / "Source.wav"
    template = tmp_path / "Template.xpj"
    output = tmp_path / "output"

    wav.write_bytes(b"fake")
    template.write_bytes(b"fake")
    output.mkdir()

    generated_xpj = output / "GUI-Test.xpj"
    generated_data = output / "GUI-Test_[ProjectData]"

    calls = {}

    def fake_generate_project_package(**kwargs):
        calls.update(kwargs)
        return generated_xpj, generated_data

    monkeypatch.setattr(
        "mpctk.gui.window.generate_project_package",
        fake_generate_project_package,
    )

    window.source_wav_edit.setText(str(wav))
    window.template_edit.setText(str(template))
    window.output_edit.setText(str(output))
    window.project_name_edit.setText("GUI-Test")
    window.source_root_combo.setCurrentText("C")
    window.target_root_combo.setCurrentText("D")
    window.scale_combo.setCurrentText("Natural Minor")
    window.bank_combo.setCurrentText("B")
    window.start_pad_spin.setValue(1)
    window.start_octave_spin.setValue(-1)

    window._generate_project()

    spec = calls["spec"]

    assert calls["source_wav"] == wav
    assert calls["template_path"] == template
    assert calls["destination_dir"] == output
    assert calls["project_name"] == "GUI-Test"
    assert calls["start_bank"] == "B"
    assert calls["start_pad"] == 1

    assert spec.source_root == "C"
    assert spec.target_root == "D"
    assert spec.layout == LAYOUT_SCALE_PADS
    assert spec.scale == "natural_minor"
    assert spec.pads == 16
    assert spec.start_octave == -1

    assert window.generated_project_path == generated_xpj
    assert window.generated_project_data_dir == generated_data
    assert window.open_finder_button.isEnabled() is True
    assert "Project generated successfully" in window.status_label.text()


def test_project_name_defaults_to_wav_stem(
    qt_app,
    monkeypatch,
    tmp_path,
):
    window = MainWindow()

    wav = tmp_path / "My Sample.wav"
    template = tmp_path / "Template.xpj"
    output = tmp_path / "output"

    wav.write_bytes(b"fake")
    template.write_bytes(b"fake")
    output.mkdir()

    calls = {}

    def fake_generate_project_package(**kwargs):
        calls.update(kwargs)
        return (
            output / "My Sample.xpj",
            output / "My Sample_[ProjectData]",
        )

    monkeypatch.setattr(
        "mpctk.gui.window.generate_project_package",
        fake_generate_project_package,
    )

    window.source_wav_edit.setText(str(wav))
    window.template_edit.setText(str(template))
    window.output_edit.setText(str(output))
    window.project_name_edit.clear()

    window._generate_project()

    assert calls["project_name"] == "My Sample"
