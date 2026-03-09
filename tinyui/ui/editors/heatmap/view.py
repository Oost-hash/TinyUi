#
#  TinyUi - Heatmap Editor View
#  Copyright (C) 2026 Oost-hash
#

from typing import List, Optional, Tuple

from PySide2.QtCore import Qt
from PySide2.QtWidgets import (
    QColorDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QVBoxLayout,
)

from .._common import QVAL_HEATMAP, UIScaler
from ..components.base_editor_view import BaseEditorView
from ..components.compact_button import CompactButton
from ..components.data_table import DataTable
from ..components.selector_bar import SelectorBar
from .viewmodel import HeatmapEditorVM


class HeatmapEditorView(BaseEditorView[HeatmapEditorVM]):
    """
    Heatmap editor view with preset selector and temperature table.
    """

    def __init__(self, parent=None):
        # Override default UI - we'll build custom layout
        QWidget.__init__(self, parent)
        self._vm: Optional[HeatmapEditorVM] = None
        self._headers = ["Temperature (°C)", "Color"]
        self._setup_heatmap_ui()

    def _setup_heatmap_ui(self):
        """Build heatmap-specific UI."""
        # Preset selector
        self._selector_bar = SelectorBar(
            self,
            buttons=[
                ("New", self._on_create_preset),
                ("Copy", self._on_copy_preset),
                ("Delete", self._on_delete_preset),
            ],
        )
        self._preset_combo = self._selector_bar.combo
        self._preset_combo.currentTextChanged.connect(self._on_preset_selected)

        # Temperature table
        self._table = DataTable(
            parent=self,
            headers=self._headers,
            column_widths={0: 120, 1: 100},
            editable_columns=[0],  # Only temp editable, color via picker
        )
        self._table.cell_edited.connect(self._on_temp_edited)
        self._table.cellClicked.connect(self._on_cell_clicked)

        # Button bar
        btn_layout = QHBoxLayout()
        for label, callback in [
            ("Add", self._on_add_temp),
            ("Sort", self._on_sort),
            ("Remove", self._on_remove_temps),
            ("Offset", self._on_offset),
            ("Reset", self._on_reset_preset),
        ]:
            btn = CompactButton(label)
            btn.clicked.connect(callback)
            btn_layout.addWidget(btn)

        btn_layout.addStretch()

        # Save/Close buttons
        self._btn_save = CompactButton("Save")
        self._btn_save.setEnabled(False)
        self._btn_save.clicked.connect(self._on_save)

        self._btn_apply = CompactButton("Apply")
        self._btn_apply.clicked.connect(self._on_apply)

        self._btn_close = CompactButton("Close")
        self._btn_close.clicked.connect(self.close)

        btn_layout.addWidget(self._btn_apply)
        btn_layout.addWidget(self._btn_save)
        btn_layout.addWidget(self._btn_close)

        # Main layout
        layout = QVBoxLayout()
        layout.addWidget(self._selector_bar)
        layout.addWidget(self._table)
        layout.addLayout(btn_layout)
        layout.setContentsMargins(10, 10, 10, 10)
        self.setLayout(layout)

        self.setWindowTitle("Heatmap Editor")
        self.setMinimumWidth(UIScaler.size(35))

    def bind_to(self, vm: HeatmapEditorVM):
        """Bind to viewmodel."""
        self._vm = vm

        # Connect VM signals
        vm.data_changed.connect(self._refresh_preset_list)
        vm.preset_list_changed.connect(self._update_preset_combo)
        vm.preset_selected.connect(self._refresh_table)
        vm.entry_added.connect(self._on_entry_added)
        vm.entry_removed.connect(self._on_entry_removed)
        vm.entries_sorted.connect(self._refresh_table)
        vm.modified_changed.connect(self._on_modified_changed)
        vm.error_occurred.connect(self._show_error)
        vm.operation_completed.connect(self._show_success)

        # Initial load
        if vm.load():
            self._refresh_preset_list()

    def _refresh_preset_list(self):
        """Update preset dropdown with current list."""
        if self._vm:
            self._update_preset_combo(self._vm.preset_names)
            # Restore selection
            current = self._vm.selected_preset_name
            if current:
                self._preset_combo.setCurrentText(current)

    def _update_preset_combo(self, names: List[str]):
        """Update combo items."""
        current = self._preset_combo.currentText()
        self._preset_combo.clear()
        self._preset_combo.addItems(names)
        if current in names:
            self._preset_combo.setCurrentText(current)

    def _refresh_table(self, preset_name: Optional[str] = None):
        """Refresh temperature table."""
        if not self._vm:
            return

        self._table.clear_rows()
        entries = self._vm.get_entries()

        for row_idx, (temp, color) in enumerate(entries):
            self._insert_temp_row(row_idx, temp, color)

    def _insert_temp_row(self, row: int, temp: float, color: str):
        """Insert row with temp item and color button."""
        from ..components.table_items import FloatTableItem

        # Temperature cell (editable float)
        temp_item = FloatTableItem(temp)
        temp_item.setData(Qt.UserRole, temp)  # Store original temp for lookup
        self._table.setItem(row, 0, temp_item)

        # Color cell (button showing color)
        color_btn = CompactButton(color)
        color_btn.setStyleSheet(f"background-color: {color}; color: #000000;")
        color_btn.clicked.connect(lambda: self._pick_color(row))
        self._table.setCellWidget(row, 1, color_btn)

    def _on_preset_selected(self, name: str):
        """User selected different preset from combo."""
        if self._vm and name:
            self._vm.select_preset(name)

    def _on_temp_edited(self, row: int, col: int, value: str):
        """Temperature value changed."""
        if col != 0 or not self._vm:
            return

        try:
            new_temp = float(value)
            item = self._table.item(row, 0)
            old_temp = item.data(Qt.UserRole) if item else new_temp

            # Get current color from button
            btn = self._table.cellWidget(row, 1)
            color = btn.text() if btn else "#FFFFFF"

            self._vm.update_temperature(old_temp, new_temp, color)

        except ValueError:
            self._show_error("Invalid temperature value")
            self._refresh_table()  # Revert

    def _on_cell_clicked(self, row: int, col: int):
        """Handle cell click - color picker on color column."""
        if col == 1:
            self._pick_color(row)

    def _pick_color(self, row: int):
        """Open color picker for row."""
        if not self._vm:
            return

        # Get current temp
        temp_item = self._table.item(row, 0)
        if not temp_item:
            return
        temp = temp_item.data(Qt.UserRole)

        # Get current color
        btn = self._table.cellWidget(row, 1)
        current_color = btn.text() if btn else "#FFFFFF"

        # Open picker
        color = QColorDialog.getColor(Qt.GlobalColor.white, self, "Select Color")
        if color.isValid():
            hex_color = color.name().upper()
            self._vm.update_color(temp, hex_color)

            # Update button
            btn.setText(hex_color)
            btn.setStyleSheet(f"background-color: {hex_color}; color: #000000;")

    def _on_entry_added(self, temp: float, color: str):
        """New entry added - append to table."""
        row = self._table.rowCount()
        self._insert_temp_row(row, temp, color)
        self._table.setCurrentCell(row, 0)

    def _on_entry_removed(self, temp: float):
        """Entry removed - full refresh (simpler than selective delete)."""
        self._refresh_table()

    def _on_add_temp(self):
        """Add new temperature."""
        if self._vm:
            self._vm.add_temperature()

    def _on_sort(self):
        """Sort temperatures."""
        if self._vm:
            self._vm.sort_temperatures()

    def _on_remove_temps(self):
        """Remove selected temperatures."""
        if not self._vm:
            return

        selected = self._table.selectedIndexes()
        if not selected:
            QMessageBox.warning(self, "Error", "No temperature selected.")
            return

        # Confirm
        reply = QMessageBox.question(
            self,
            "Confirm",
            "<b>Delete selected temperatures?</b>",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        # Collect temps to delete
        temps = []
        for idx in selected:
            item = self._table.item(idx.row(), 0)
            if item:
                temp = item.data(Qt.UserRole)
                temps.append(temp)

        self._vm.remove_temperatures(temps)

    def _on_offset(self):
        """Open offset dialog."""
        if not self._vm:
            return

        # Check selection
        selected = self._table.selectedIndexes()
        if not selected:
            QMessageBox.warning(
                self, "Error", "Select one or more temperatures to apply offset."
            )
            return

        # Collect selected temps
        temps = []
        for idx in selected:
            if idx.column() == 0:  # Only temp column
                item = self._table.item(idx.row(), 0)
                if item:
                    temps.append(item.data(Qt.UserRole))

        if not temps:
            return

        # Simple offset dialog (could be separate component)
        from .._editor_common import BatchOffset

        dialog = BatchOffset(
            self, lambda offset, scale: self._vm.apply_offset(temps, offset, scale)
        )
        dialog.config(decimals=1, step=1.0, min_range=-99999, max_range=99999)
        dialog.open()

    def _on_reset_preset(self):
        """Reset current preset to default."""
        if not self._vm or not self._vm.selected_preset_name:
            return

        name = self._vm.selected_preset_name
        if self._vm.is_builtin_preset:
            QMessageBox.warning(self, "Error", "Cannot reset built-in preset.")
            return

        reply = QMessageBox.question(
            self,
            "Confirm",
            f"<b>Reset {name} to default?</b><br><br>"
            "Changes are only saved after clicking Apply or Save.",
        )
        if reply == QMessageBox.Yes:
            self._vm.reset_preset(name)

    def _on_create_preset(self):
        """Create new preset dialog."""
        dialog = _CreatePresetDialog(self, "Create Heatmap Preset", self._vm)
        dialog.exec_()

    def _on_copy_preset(self):
        """Copy preset dialog."""
        if not self._vm or not self._vm.selected_preset_name:
            return
        dialog = _CreatePresetDialog(
            self,
            "Duplicate Heatmap Preset",
            self._vm,
            source_preset=self._vm.selected_preset_name,
        )
        dialog.exec_()

    def _on_delete_preset(self):
        """Delete current preset."""
        if not self._vm or not self._vm.selected_preset_name:
            return

        name = self._vm.selected_preset_name
        if self._vm.is_builtin_preset:
            QMessageBox.warning(self, "Error", "Cannot delete built-in preset.")
            return

        reply = QMessageBox.question(
            self,
            "Confirm",
            f"<b>Delete {name}?</b><br><br>"
            "Changes are only saved after clicking Apply or Save.",
        )
        if reply == QMessageBox.Yes:
            self._vm.delete_preset(name)

    def _on_save(self):
        """Save changes."""
        if self._vm:
            self._vm.save()

    def _on_apply(self):
        """Apply changes without closing."""
        self._on_save()

    def _on_modified_changed(self, is_modified: bool):
        """Update save button state."""
        self._btn_save.setEnabled(is_modified)
        self._btn_apply.setEnabled(is_modified)


class _CreatePresetDialog(QMessageBox):
    """Internal dialog for creating/copying presets."""

    def __init__(
        self,
        parent,
        title: str,
        vm: HeatmapEditorVM,
        source_preset: Optional[str] = None,
    ):
        super().__init__(parent)
        self._vm = vm
        self._source = source_preset

        self.setWindowTitle(title)

        # Custom layout with line edit
        self._edit = QLineEdit()
        self._edit.setMaxLength(40)
        self._edit.setPlaceholderText("Enter preset name")
        self._edit.setValidator(QVAL_HEATMAP)

        # Build dialog
        layout = QVBoxLayout()
        layout.addWidget(self._edit)

        # Add standard buttons
        self.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        self.setDefaultButton(QMessageBox.Ok)

        # Insert custom widget
        # Note: QMessageBox layout is tricky, use simple approach
        self.layout().insertLayout(0, layout)

        self.setText(f"{'Copy' if source_preset else 'Create'} preset:")
        self.setInformativeText(
            f"Source: {source_preset}" if source_preset else "Create new empty preset"
        )

    def accept(self):
        """Handle OK."""
        name = self._edit.text()
        if not name:
            QMessageBox.warning(self, "Error", "Invalid preset name.")
            return

        if self._source:
            success = self._vm.copy_preset(self._source, name)
        else:
            success = self._vm.create_preset(name)

        if success:
            super().accept()
