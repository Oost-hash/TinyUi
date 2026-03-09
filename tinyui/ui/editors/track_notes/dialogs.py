#
#  TinyUi - Track Notes Dialogs
#  Copyright (C) 2026 Oost-hash
#

import re
from typing import Callable, Dict, List

from PySide2.QtCore import Qt
from PySide2.QtWidgets import (
    QCheckBox,
    QDialogButtonBox,
    QDoubleSpinBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

from ui.common import BaseDialog, UIScaler


class BatchOffsetDialog(BaseDialog):
    """Batch offset dialog for track notes distances."""

    def __init__(self, parent, offset_func: Callable[[float, bool], None]):
        super().__init__(parent)
        self.setWindowTitle("Batch Offset")
        self._offset_func = offset_func

        # UI
        self._last_label = QLabel("Last Offset: 0")
        self._spinbox = QDoubleSpinBox()
        self._spinbox.setDecimals(2)
        self._spinbox.setRange(-99999, 99999)
        self._spinbox.setSingleStep(0.1)
        self._spinbox.setAlignment(Qt.AlignRight)

        self._scale_checkbox = QCheckBox("Scale Mode")

        buttons = QDialogButtonBox(QDialogButtonBox.Apply | QDialogButtonBox.Close)
        buttons.clicked.connect(self._on_button_clicked)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self._last_label)
        layout.addWidget(QLabel("Offset:"))
        layout.addWidget(self._spinbox)
        layout.addWidget(self._scale_checkbox)
        layout.addWidget(buttons)

        self.setLayout(layout)
        self.setFixedSize(UIScaler.size(15), self.sizeHint().height())

    def _on_button_clicked(self, button):
        if button == QDialogButtonBox.Apply:
            self._apply()
        elif button == QDialogButtonBox.Close:
            self.reject()

    def _apply(self):
        value = self._spinbox.value()
        if value != 0:
            is_scale = self._scale_checkbox.isChecked()
            self._offset_func(value, is_scale)

            label = "Last Scale:" if is_scale else "Last Offset:"
            self._last_label.setText(f"{label} {value}")
            self._spinbox.setValue(0)


class ReplaceDialog(BaseDialog):
    """Find and replace dialog for track notes."""

    def __init__(
        self,
        parent,
        column_names: List[str],
        replace_func: Callable[[int, str, str, bool, bool], None],
    ):
        super().__init__(parent)
        self.setWindowTitle("Batch Replace")

        self._replace_func = replace_func
        self._selected_column = 1  # Default to note column

        # UI
        self._column_label = QLabel("Column: Note")

        self._find_edit = QLineEdit()
        self._find_edit.setPlaceholderText("Find text")

        self._replace_edit = QLineEdit()
        self._replace_edit.setPlaceholderText("Replace with")

        self._case_checkbox = QCheckBox("Match Case")
        self._whole_checkbox = QCheckBox("Match Whole Word")

        # Column buttons
        btn_layout = QHBoxLayout()
        for i, name in enumerate(column_names):
            btn = QPushButton(name)
            btn.clicked.connect(
                lambda checked, idx=i, n=name: self._select_column(idx, n)
            )
            btn_layout.addWidget(btn)

        replace_btn = QPushButton("Replace")
        replace_btn.clicked.connect(self._replace)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.reject)

        # Layout
        grid = QGridLayout()
        grid.addWidget(QLabel("Select:"), 0, 0)
        grid.addLayout(btn_layout, 0, 1)
        grid.addWidget(self._column_label, 1, 0, 1, 2)
        grid.addWidget(QLabel("Find:"), 2, 0)
        grid.addWidget(self._find_edit, 2, 1)
        grid.addWidget(QLabel("Replace:"), 3, 0)
        grid.addWidget(self._replace_edit, 3, 1)
        grid.addWidget(self._case_checkbox, 4, 1)
        grid.addWidget(self._whole_checkbox, 5, 1)

        btn_row = QHBoxLayout()
        btn_row.addWidget(replace_btn)
        btn_row.addStretch()
        btn_row.addWidget(close_btn)

        layout = QVBoxLayout()
        layout.addLayout(grid)
        layout.addLayout(btn_row)

        self.setLayout(layout)
        self.setMinimumWidth(UIScaler.size(25))

    def _select_column(self, index: int, name: str):
        self._selected_column = index
        self._column_label.setText(f"Column: {name}")

    def _replace(self):
        find = self._find_edit.text()
        replace = self._replace_edit.text()

        if not find:
            return

        self._replace_func(
            self._selected_column,
            find,
            replace,
            self._case_checkbox.isChecked(),
            self._whole_checkbox.isChecked(),
        )


class MetadataDialog(BaseDialog):
    """Metadata editor for track notes."""

    STANDARD_FIELDS = [
        ("track_name", "Track Name"),
        ("track_layout", "Track Layout"),
        ("author", "Author"),
        ("description", "Description"),
    ]

    def __init__(
        self,
        parent,
        metadata: Dict[str, str],
        on_save: Callable[[Dict[str, str]], None],
    ):
        super().__init__(parent)
        self.setWindowTitle("Track Notes Info")

        self._on_save = on_save
        self._fields = {}

        # Layout
        grid = QGridLayout()

        # Standard fields
        for row, (key, label) in enumerate(self.STANDARD_FIELDS):
            grid.addWidget(QLabel(f"{label}:"), row, 0)
            edit = QLineEdit(metadata.get(key, ""))
            self._fields[key] = edit
            grid.addWidget(edit, row, 1)

        # Custom fields (any metadata not in standard fields)
        custom_start = len(self.STANDARD_FIELDS)
        custom_row = 0
        for key, value in metadata.items():
            if key not in [f[0] for f in self.STANDARD_FIELDS]:
                grid.addWidget(QLabel(f"{key}:"), custom_start + custom_row, 0)
                edit = QLineEdit(str(value))
                self._fields[key] = edit
                grid.addWidget(edit, custom_start + custom_row, 1)
                custom_row += 1

        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._save)
        buttons.rejected.connect(self.reject)

        main_layout = QVBoxLayout()
        main_layout.addLayout(grid)
        main_layout.addWidget(buttons)

        self.setLayout(layout)
        self.setMinimumWidth(UIScaler.size(30))

    def _save(self):
        updated = {key: edit.text() for key, edit in self._fields.items()}
        self._on_save(updated)
        self.accept()
