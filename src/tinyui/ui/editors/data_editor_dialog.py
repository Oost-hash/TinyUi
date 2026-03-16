"""DataEditorDialog — generic preset-based data editor.

Takes an EditorSpec (registered by a plugin) and builds a complete
editor dialog with preset selector, table editor, and save/close buttons.
"""

from __future__ import annotations

import copy
from typing import TYPE_CHECKING

from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from tinycore.editor import EditorSpec

from ..components.table_editor.column_spec import ColumnSpec
from ..components.table_editor.editor_viewmodel import EditorViewModel
from ..components.table_editor.table_editor import TableEditor
from ..components.table_editor.table_model import TableModel

if TYPE_CHECKING:
    from tinycore import App


class DataEditorDialog(QWidget):
    """Generic data editor driven by an EditorSpec.

    Reads data from ConfigStore, shows a preset selector + table editor,
    and writes changes back to the store on save.
    """

    def __init__(self, core: App, spec: EditorSpec, parent=None):
        super().__init__(parent)
        self._core = core
        self._spec = spec
        self.setWindowTitle(spec.title)

        # Get data from config store
        self._data: dict[str, dict] = copy.deepcopy(
            core.config.get(spec.config_key)
        )
        self._current_key = next(iter(self._data.keys()))

        # Convert EditorSpec columns to TableEditor ColumnSpecs
        self._col_specs = [
            ColumnSpec(
                name=col.name,
                data_type=col.data_type,
                editable=col.editable,
                width=col.width,
                default_value=col.default_value,
                widget=col.widget,
            )
            for col in spec.columns
        ]

        self._setup_editor()
        if spec.has_presets:
            self._setup_preset_selector()
        self._setup_layout()
        self._load_preset(self._current_key)

    def _setup_editor(self):
        self._model = TableModel(self._col_specs)

        def save(data: list[dict]) -> bool:
            self._data[self._current_key] = {
                str(row[self._col_specs[0].name]): row[self._col_specs[1].name]
                for row in data
            } if len(self._col_specs) == 2 else {
                str(i): row for i, row in enumerate(data)
            }
            self._core.config.update(self._spec.config_key, copy.deepcopy(self._data))
            return True

        self._vm = EditorViewModel(self._model, save)
        self._table = TableEditor(self._vm)

    def _setup_preset_selector(self):
        self._preset_combo = QComboBox()
        self._preset_combo.addItems(self._data.keys())
        self._preset_combo.currentTextChanged.connect(self._on_preset_changed)

        self._btn_new = QPushButton("New")
        self._btn_copy = QPushButton("Copy")
        self._btn_delete = QPushButton("Delete")

        self._btn_new.clicked.connect(self._on_new_preset)
        self._btn_copy.clicked.connect(self._on_copy_preset)
        self._btn_delete.clicked.connect(self._on_delete_preset)

    def _setup_layout(self):
        main = QVBoxLayout()

        if self._spec.has_presets:
            top = QHBoxLayout()
            top.addWidget(QLabel("Preset:"))
            top.addWidget(self._preset_combo, stretch=1)
            top.addWidget(self._btn_new)
            top.addWidget(self._btn_copy)
            top.addWidget(self._btn_delete)
            main.addLayout(top)

        main.addWidget(self._table, stretch=1)

        bottom = QHBoxLayout()
        btn_apply = QPushButton("Apply")
        btn_save = QPushButton("Save && Close")
        btn_close = QPushButton("Close")

        btn_apply.clicked.connect(self._vm.save)
        btn_save.clicked.connect(self._on_save_close)
        btn_close.clicked.connect(self.close)

        bottom.addStretch()
        bottom.addWidget(btn_apply)
        bottom.addWidget(btn_save)
        bottom.addWidget(btn_close)
        main.addLayout(bottom)

        self.setLayout(main)
        self.resize(500, 400)

    def _load_preset(self, key: str):
        self._current_key = key
        raw = self._data.get(key, {})

        # Convert dict[key, value] to list[dict] for the table
        col_names = [c.name for c in self._col_specs]
        if len(col_names) == 2:
            data = [
                {col_names[0]: k, col_names[1]: v}
                for k, v in raw.items()
            ]
        else:
            data = [raw] if isinstance(raw, dict) else list(raw)

        self._model._data = data
        self._model._original_data = self._model.get_data()
        self._table.refresh()

    def _on_preset_changed(self, new_key: str):
        if self._vm.is_modified():
            reply = QMessageBox.question(
                self,
                "Save Changes?",
                f"Save changes to '{self._current_key}'?",
                QMessageBox.StandardButton.Save
                | QMessageBox.StandardButton.Discard
                | QMessageBox.StandardButton.Cancel,
            )
            if reply == QMessageBox.StandardButton.Save:
                self._vm.save()
            elif reply == QMessageBox.StandardButton.Cancel:
                self._preset_combo.setCurrentText(self._current_key)
                return
        self._load_preset(new_key)

    def _on_new_preset(self):
        name, ok = QInputDialog.getText(self, "New Preset", "Name:")
        if ok and name and name not in self._data:
            # Create with one default row
            defaults = {c.name: str(c.default_value) for c in self._col_specs}
            key = str(defaults[self._col_specs[0].name])
            val = defaults[self._col_specs[1].name] if len(self._col_specs) == 2 else defaults
            self._data[name] = {key: val}
            self._preset_combo.addItem(name)
            self._preset_combo.setCurrentText(name)

    def _on_copy_preset(self):
        source = self._current_key
        new_name = f"{source}_copy"
        counter = 1
        while new_name in self._data:
            new_name = f"{source}_copy_{counter}"
            counter += 1
        self._data[new_name] = copy.deepcopy(self._data[source])
        self._preset_combo.addItem(new_name)
        self._preset_combo.setCurrentText(new_name)

    def _on_delete_preset(self):
        if len(self._data) <= 1:
            QMessageBox.warning(self, "Error", "Cannot delete last preset")
            return
        reply = QMessageBox.question(self, "Confirm", f"Delete '{self._current_key}'?")
        if reply == QMessageBox.StandardButton.Yes:
            del self._data[self._current_key]
            self._preset_combo.removeItem(self._preset_combo.currentIndex())

    def _on_save_close(self):
        self._vm.save()
        self.close()
