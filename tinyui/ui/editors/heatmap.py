# tinyui/ui/editors/heatmap_editor.py
import time
from typing import Dict, List

from PySide2.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ...adapters import cfg
from ...adapters.tinypedal.files import ConfigType
from ...adapters.tinypedal.settings import copy_setting
from ..components.column_spec import ColumnSpec, Validators
from ..components.editor_viewmodel import EditorViewModel
from ..components.table_editor import TableEditor
from ..components.table_model import TableModel


class HeatmapEditor(QWidget):
    """
    Heatmap editor - configureer temperatuur-kleur mappings.

    Gebruikt generieke TableEditor voor CRUD/sort/batch.
    Alleen specifiek: preset selector + kleur preview.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Heatmap Editor")

        # 1. Kopieer data (voor revert mogelijkheid)
        self._heatmaps = copy_setting(cfg.user.heatmap)
        self._current_key = next(iter(self._heatmaps.keys()))

        # 2. Bouw generieke editor
        self._setup_editor()

        # 3. Specifieke UI: preset selector
        self._setup_preset_selector()

        # 4. Layout
        self._setup_layout()

        # 5. Laad eerste preset
        self._load_preset(self._current_key)

    def _setup_editor(self):
        """Bouw generieke TableEditor"""
        # Column configuratie
        columns = [
            ColumnSpec(
                name="temperature",
                data_type=float,
                editable=True,
                width=100,
                default_value=0.0,
            ),
            ColumnSpec(
                name="color",
                data_type=str,
                editable=True,
                validator=Validators.hex_color,
                default_value="#FFFFFF",
            ),
        ]

        # Model (leeg, wordt gevuld bij preset switch)
        self._model = TableModel(columns)

        # Saver functie
        def save_heatmap(data: List[Dict]) -> bool:
            # Converteer list naar dict formaat
            self._heatmaps[self._current_key] = {
                str(row["temperature"]): row["color"] for row in data
            }
            cfg.user.heatmap = copy_setting(self._heatmaps)
            cfg.save(0, cfg_type=ConfigType.HEATMAP)
            while cfg.is_saving:
                time.sleep(0.01)
            return True

        # ViewModel + TableEditor
        self._vm = EditorViewModel(self._model, save_heatmap)
        self._table = TableEditor(self._vm)

    def _setup_preset_selector(self):
        """Specifiek: preset selector met New/Copy/Delete"""
        self._preset_combo = QComboBox()
        self._preset_combo.addItems(self._heatmaps.keys())
        self._preset_combo.currentTextChanged.connect(self._on_preset_changed)

        self._btn_new = QPushButton("New")
        self._btn_copy = QPushButton("Copy")
        self._btn_delete = QPushButton("Delete")

        self._btn_new.clicked.connect(self._on_new_preset)
        self._btn_copy.clicked.connect(self._on_copy_preset)
        self._btn_delete.clicked.connect(self._on_delete_preset)

    def _setup_layout(self):
        """Layout alle componenten"""
        # Top bar: preset selector
        top = QHBoxLayout()
        top.addWidget(QLabel("Preset:"))
        top.addWidget(self._preset_combo, stretch=1)
        top.addWidget(self._btn_new)
        top.addWidget(self._btn_copy)
        top.addWidget(self._btn_delete)

        # Bottom bar: actions
        bottom = QHBoxLayout()
        self._btn_apply = QPushButton("Apply")
        self._btn_save = QPushButton("Save")
        self._btn_close = QPushButton("Close")

        self._btn_apply.clicked.connect(self._vm.save)
        self._btn_save.clicked.connect(self._on_save_close)
        self._btn_close.clicked.connect(self.close)

        bottom.addStretch()
        bottom.addWidget(self._btn_apply)
        bottom.addWidget(self._btn_save)
        bottom.addWidget(self._btn_close)

        # Main
        main = QVBoxLayout()
        main.addLayout(top)
        main.addWidget(self._table, stretch=1)
        main.addLayout(bottom)

        self.setLayout(main)
        self.resize(400, 400)

    def _load_preset(self, key: str):
        """Laad preset data in model"""
        self._current_key = key

        # Converteer dict naar list
        data = [
            {"temperature": float(k), "color": v}
            for k, v in self._heatmaps.get(key, {}).items()
        ]

        # Reset model met nieuwe data
        self._model._data = data
        self._model._original_data = self._model.get_data()
        self._table.refresh()

    def _on_preset_changed(self, new_key: str):
        """Switch preset met modified check"""
        if self._vm.is_modified():
            reply = QMessageBox.question(
                self,
                "Save Changes?",
                f"Save changes to '{self._current_key}'?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
            )
            if reply == QMessageBox.Save:
                self._vm.save()
            elif reply == QMessageBox.Cancel:
                self._preset_combo.setCurrentText(self._current_key)
                return

        self._load_preset(new_key)

    def _on_new_preset(self):
        """Maak nieuwe preset"""
        from PySide2.QtWidgets import QInputDialog

        name, ok = QInputDialog.getText(self, "New Preset", "Name:")
        if ok and name and name not in self._heatmaps:
            self._heatmaps[name] = {"-273.0": "#4444FF"}
            self._preset_combo.addItem(name)
            self._preset_combo.setCurrentText(name)

    def _on_copy_preset(self):
        """Dupliceer huidige preset"""
        source = self._current_key
        new_name = f"{source}_copy"
        counter = 1
        while new_name in self._heatmaps:
            new_name = f"{source}_copy_{counter}"
            counter += 1

        self._heatmaps[new_name] = copy_setting(self._heatmaps[source])
        self._preset_combo.addItem(new_name)
        self._preset_combo.setCurrentText(new_name)

    def _on_delete_preset(self):
        """Verwijder preset (niet built-in)"""
        if self._current_key in cfg.default.heatmap:
            QMessageBox.warning(self, "Error", "Cannot delete built-in preset")
            return

        reply = QMessageBox.question(self, "Confirm", f"Delete '{self._current_key}'?")
        if reply == QMessageBox.Yes:
            del self._heatmaps[self._current_key]
            self._preset_combo.removeItem(self._preset_combo.currentIndex())

    def _on_save_close(self):
        self._vm.save()
        self.close()
