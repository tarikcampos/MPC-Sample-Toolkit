from __future__ import annotations

import subprocess
from pathlib import Path

from PySide6.QtCore import QSettings, Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFormLayout,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from mpctk.generation import BANK_NAMES, generate_project_package
from mpctk.music import (
    BankSpec,
    LAYOUT_CHROMATIC_KEYBOARD,
    LAYOUT_SCALE_PADS,
)


NOTE_NAMES = (
    "C",
    "C#",
    "D",
    "D#",
    "E",
    "F",
    "F#",
    "G",
    "G#",
    "A",
    "A#",
    "B",
)

LAYOUTS = {
    "Scale Pads": LAYOUT_SCALE_PADS,
    "Chromatic Keyboard": LAYOUT_CHROMATIC_KEYBOARD,
}

SCALES = {
    "Major": "major",
    "Natural Minor": "natural_minor",
}


class MainWindow(QMainWindow):
    """Main MPCTK project-generation window."""

    def __init__(self) -> None:
        super().__init__()

        self.generated_project_path: Path | None = None
        self.generated_project_data_dir: Path | None = None

        self.setWindowTitle("MPC Sample Toolkit")
        self.setMinimumSize(760, 700)
        self.resize(820, 740)

        self._apply_styles()
        self._build_ui()
        self._update_layout_controls()

    def _apply_styles(self) -> None:
        self.setStyleSheet(
            """
            QMainWindow {
                background: #353535;
            }

            QLabel {
                color: #f2f2f2;
            }

            QLineEdit {
                padding: 0 10px;
                background: #242424;
                color: #f4f4f4;
                border: 1px solid #5a5a5a;
                border-radius: 6px;
            }

            QLineEdit:focus {
                border: 1px solid #8a8a8a;
            }

            QPushButton {
                min-height: 32px;
                padding: 0 14px;
                background: #555555;
                color: #f5f5f5;
                border: 1px solid #696969;
                border-radius: 6px;
                font-weight: 600;
            }

            QPushButton:hover {
                background: #626262;
            }

            QPushButton:pressed {
                background: #484848;
            }

            QPushButton:disabled {
                color: #888888;
                background: #3d3d3d;
                border-color: #4b4b4b;
            }
            """
        )

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)

        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(36, 28, 36, 28)
        root_layout.setSpacing(12)

        title = QLabel("MPC Sample Toolkit")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(
            "font-size: 24px; font-weight: 700;"
        )
        root_layout.addWidget(title)

        subtitle = QLabel(
            "Generate playable Akai MPC Sample projects from WAV files."
        )
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet(
            "font-size: 14px; color: #aaaaaa;"
        )
        root_layout.addWidget(subtitle)

        root_layout.addSpacing(14)

        # Project source
        root_layout.addWidget(self._section_heading("PROJECT SOURCE"))

        source_form = self._new_form()
        root_layout.addLayout(source_form)

        self.source_wav_edit = QLineEdit()
        source_form.addRow(
            "Source WAV",
            self._file_row(
                self.source_wav_edit,
                self._browse_source_wav,
                "Browse…",
            ),
        )

        self.template_edit = QLineEdit()
        source_form.addRow(
            "XPJ Template",
            self._file_row(
                self.template_edit,
                self._browse_template,
                "Browse…",
            ),
        )

        root_layout.addSpacing(12)

        # Musical layout
        root_layout.addWidget(self._section_heading("MUSICAL LAYOUT"))

        music_panel = QWidget()
        music_panel.setObjectName("musicPanel")
        music_panel.setStyleSheet(
            "QWidget#musicPanel {"
            "background: #303030;"
            "border: 1px solid #505050;"
            "border-radius: 8px;"
            "}"
        )

        music_panel_layout = QGridLayout(music_panel)
        music_panel_layout.setContentsMargins(24, 18, 24, 20)
        music_panel_layout.setHorizontalSpacing(42)
        music_panel_layout.setVerticalSpacing(10)
        music_panel_layout.setColumnStretch(0, 1)
        music_panel_layout.setColumnStretch(1, 1)

        musical_heading = QLabel("MUSICAL SETUP")
        musical_heading.setStyleSheet(
            "font-size: 10px; font-weight: 700; color: #aaaaaa;"
        )
        music_panel_layout.addWidget(musical_heading, 0, 0)

        pad_heading = QLabel("PAD BANK")
        pad_heading.setStyleSheet(
            "font-size: 10px; font-weight: 700; color: #aaaaaa;"
        )
        music_panel_layout.addWidget(pad_heading, 0, 1)

        left_grid = QGridLayout()
        left_grid.setHorizontalSpacing(14)
        left_grid.setVerticalSpacing(9)
        left_grid.setColumnStretch(1, 1)

        right_grid = QGridLayout()
        right_grid.setHorizontalSpacing(14)
        right_grid.setVerticalSpacing(9)
        right_grid.setColumnStretch(1, 1)

        self.source_root_combo = QComboBox()
        self.source_root_combo.addItems(NOTE_NAMES)
        self.source_root_combo.setMinimumWidth(160)

        left_grid.addWidget(
            QLabel("Source Root"),
            0,
            0,
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
        )
        left_grid.addWidget(self.source_root_combo, 0, 1)

        self.target_root_combo = QComboBox()
        self.target_root_combo.addItems(NOTE_NAMES)
        self.target_root_combo.setMinimumWidth(160)

        left_grid.addWidget(
            QLabel("Target Root"),
            1,
            0,
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
        )
        left_grid.addWidget(self.target_root_combo, 1, 1)

        self.layout_combo = QComboBox()
        self.layout_combo.addItems(LAYOUTS)
        self.layout_combo.setMinimumWidth(160)
        self.layout_combo.currentTextChanged.connect(
            self._update_layout_controls
        )

        left_grid.addWidget(
            QLabel("Layout"),
            2,
            0,
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
        )
        left_grid.addWidget(self.layout_combo, 2, 1)

        self.scale_combo = QComboBox()
        self.scale_combo.addItems(SCALES)
        self.scale_combo.setMinimumWidth(160)

        left_grid.addWidget(
            QLabel("Scale"),
            3,
            0,
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
        )
        left_grid.addWidget(self.scale_combo, 3, 1)

        self.pads_spin = QSpinBox()
        self.pads_spin.setRange(1, 128)
        self.pads_spin.setMinimumWidth(130)
        self.pads_spin.setValue(16)

        right_grid.addWidget(
            QLabel("Pads"),
            0,
            0,
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
        )
        right_grid.addWidget(self.pads_spin, 0, 1)

        self.bank_combo = QComboBox()
        self.bank_combo.addItems(BANK_NAMES)
        self.bank_combo.setMinimumWidth(130)

        right_grid.addWidget(
            QLabel("Start Bank"),
            1,
            0,
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
        )
        right_grid.addWidget(self.bank_combo, 1, 1)

        self.start_pad_spin = QSpinBox()
        self.start_pad_spin.setRange(1, 16)
        self.start_pad_spin.setMinimumWidth(130)
        self.start_pad_spin.setValue(1)

        right_grid.addWidget(
            QLabel("Start Pad"),
            2,
            0,
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
        )
        right_grid.addWidget(self.start_pad_spin, 2, 1)

        self.start_octave_spin = QSpinBox()
        self.start_octave_spin.setRange(-8, 8)
        self.start_octave_spin.setMinimumWidth(130)
        self.start_octave_spin.setValue(0)

        right_grid.addWidget(
            QLabel("Start Octave"),
            3,
            0,
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
        )
        right_grid.addWidget(self.start_octave_spin, 3, 1)

        left_widget = QWidget()
        left_widget.setLayout(left_grid)

        right_widget = QWidget()
        right_widget.setLayout(right_grid)

        music_panel_layout.addWidget(left_widget, 1, 0)
        music_panel_layout.addWidget(right_widget, 1, 1)

        root_layout.addWidget(music_panel)
        root_layout.addSpacing(12)

        # Output
        root_layout.addWidget(self._section_heading("OUTPUT"))

        output_form = self._new_form()
        root_layout.addLayout(output_form)

        self.project_name_edit = QLineEdit()
        self.project_name_edit.setPlaceholderText(
            "Defaults to the source WAV filename"
        )
        output_form.addRow("Project Name", self.project_name_edit)

        self.output_edit = QLineEdit()
        output_form.addRow(
            "Destination",
            self._file_row(
                self.output_edit,
                self._browse_output,
                "Browse…",
            ),
        )

        root_layout.addSpacing(14)

        self.generate_button = QPushButton("Generate Project")
        self.generate_button.setFixedSize(300, 48)
        self.generate_button.setStyleSheet(
            "QPushButton {"
            "background: #b9782d;"
            "color: #ffffff;"
            "border: 1px solid #cf9148;"
            "border-radius: 7px;"
            "font-size: 14px;"
            "font-weight: 700;"
            "}"
            "QPushButton:hover {"
            "background: #c88735;"
            "}"
            "QPushButton:disabled {"
            "background: #666666;"
            "color: #bdbdbd;"
            "border-color: #747474;"
            "}"
        )
        self.generate_button.clicked.connect(self._generate_project)

        generate_row = QHBoxLayout()
        generate_row.addStretch()
        generate_row.addWidget(self.generate_button)
        generate_row.addStretch()
        root_layout.addLayout(generate_row)

        root_layout.addSpacing(5)

        result_panel = QWidget()
        result_panel.setObjectName("resultPanel")
        result_panel.setStyleSheet(
            "QWidget#resultPanel {"
            "background: #303030;"
            "border: 1px solid #505050;"
            "border-radius: 8px;"
            "}"
        )

        result_layout = QHBoxLayout(result_panel)
        result_layout.setContentsMargins(16, 11, 12, 11)
        result_layout.setSpacing(14)

        self.status_label = QLabel("Ready.")
        self.status_label.setWordWrap(True)
        self.status_label.setMinimumHeight(36)
        self.status_label.setStyleSheet("color: #bdbdbd;")
        result_layout.addWidget(self.status_label, 1)

        self.open_finder_button = QPushButton("Open in Finder")
        self.open_finder_button.setMinimumSize(145, 36)
        self.open_finder_button.setEnabled(False)
        self.open_finder_button.clicked.connect(self._open_in_finder)
        result_layout.addWidget(self.open_finder_button)

        root_layout.addWidget(result_panel)

    def _section_heading(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setStyleSheet(
            "font-size: 11px; font-weight: 700; color: #999999;"
        )
        return label

    def _new_form(self) -> QFormLayout:
        form = QFormLayout()
        form.setHorizontalSpacing(22)
        form.setVerticalSpacing(10)
        form.setFieldGrowthPolicy(
            QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow
        )
        form.setLabelAlignment(
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignVCenter
        )
        return form

    def _file_row(
        self,
        line_edit: QLineEdit,
        callback,
        button_text: str,
    ) -> QWidget:
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        layout.addWidget(line_edit, 1)

        button = QPushButton(button_text)
        button.setMinimumWidth(96)
        button.clicked.connect(callback)
        layout.addWidget(button)

        return container

    def _browse_source_wav(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Source WAV",
            "",
            "WAV Audio (*.wav *.WAV)",
        )

        if path:
            self.source_wav_edit.setText(path)

            if not self.project_name_edit.text().strip():
                self.project_name_edit.setText(Path(path).stem)

    def _browse_template(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select XPJ Template",
            "",
            "MPC Project (*.xpj)",
        )

        if path:
            self.template_edit.setText(path)

    def _browse_output(self) -> None:
        path = QFileDialog.getExistingDirectory(
            self,
            "Select Destination Directory",
        )

        if path:
            self.output_edit.setText(path)

    def _update_layout_controls(self) -> None:
        is_scale_layout = (
            LAYOUTS.get(self.layout_combo.currentText())
            == LAYOUT_SCALE_PADS
        )
        self.scale_combo.setEnabled(is_scale_layout)

    def _build_spec(self) -> BankSpec:
        layout = LAYOUTS[self.layout_combo.currentText()]

        scale = (
            SCALES[self.scale_combo.currentText()]
            if layout == LAYOUT_SCALE_PADS
            else None
        )

        return BankSpec(
            source_root=self.source_root_combo.currentText(),
            target_root=self.target_root_combo.currentText(),
            layout=layout,
            pads=self.pads_spin.value(),
            scale=scale,
            start_octave=self.start_octave_spin.value(),
        )

    def _set_status(self, text: str, state: str = "neutral") -> None:
        colors = {
            "neutral": "#f2f2f2",
            "working": "#d8d8d8",
            "success": "#8fd694",
            "error": "#ff9a9a",
        }
        self.status_label.setStyleSheet(
            f"color: {colors.get(state, colors["neutral"])};"
        )
        self.status_label.setText(text)

    def _generate_project(self) -> None:
        self.open_finder_button.setEnabled(False)
        self.generated_project_path = None
        self.generated_project_data_dir = None

        source_wav_text = self.source_wav_edit.text().strip()
        template_text = self.template_edit.text().strip()
        output_text = self.output_edit.text().strip()

        if not source_wav_text:
            self._set_status("Source WAV is required.", "error")
            return

        if not template_text:
            self._set_status("XPJ template is required.", "error")
            return

        if not output_text:
            self._set_status(
                "Destination directory is required.",
                "error",
            )
            return

        source_wav = Path(source_wav_text)
        template = Path(template_text)
        output = Path(output_text)

        project_name = (
            self.project_name_edit.text().strip()
            or source_wav.stem
        )

        try:
            spec = self._build_spec()

            project_path, project_data_dir = (
                generate_project_package(
                    source_wav=source_wav,
                    template_path=template,
                    destination_dir=output,
                    project_name=project_name,
                    spec=spec,
                    start_bank=self.bank_combo.currentText(),
                    start_pad=self.start_pad_spin.value(),
                )
            )
        except (
            FileExistsError,
            FileNotFoundError,
            IndexError,
            TypeError,
            ValueError,
        ) as exc:
            self.status_label.setText(
                f"Generation failed: {exc}"
            )
            return

        self.generated_project_path = project_path
        self.generated_project_data_dir = project_data_dir

        self.status_label.setText(
            "Project generated successfully.\n"
            f"XPJ: {project_path}\n"
            f"ProjectData: {project_data_dir}"
        )

        self.open_finder_button.setEnabled(True)

    def _open_in_finder(self) -> None:
        if self.generated_project_path is None:
            return

        subprocess.run(
            ["open", "-R", str(self.generated_project_path)],
            check=False,
        )
