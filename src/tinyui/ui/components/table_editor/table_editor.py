#  TinyUI
#  Copyright (C) 2026 Oost-hash
#
#  This file is part of TinyUI.
#
#  TinyUI is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  TinyUI is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#  TinyUI builds on TinyPedal by s-victor (https://github.com/s-victor/TinyPedal),
#  licensed under GPLv3.

# tinyui/ui/components/table_editor.py
from typing import List, Optional

from PySide6.QtCore import QPoint, Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QMenu,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
)

from .column_spec import ColumnSpec
from .editor_viewmodel import EditorViewModel


class TableEditor(QTableWidget):
    """
    Generieke table editor component.

    Werkt met EditorViewModel voor alle logica.
    Rendert kolommen volgens ColumnSpec.
    """

    def __init__(
        self,
        viewmodel: EditorViewModel,
        parent=None,
        enable_add: bool = True,
        enable_delete: bool = True,
        enable_sort: bool = True,
        enable_batch: bool = True,
    ):
        super().__init__(parent)

        self._vm = viewmodel
        self._enable_add = enable_add
        self._enable_delete = enable_delete
        self._enable_sort = enable_sort
        self._enable_batch = enable_batch

        self._setup_appearance()
        self._build_columns()
        self._connect_signals()

        # Initial load
        self.refresh()

    def _setup_appearance(self):
        """Configureer table look & feel"""
        self.verticalHeader().setVisible(False)
        self.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.setAlternatingRowColors(True)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)

        # Context menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)

        # Cell edit tracking
        self.cellChanged.connect(self._on_cell_changed)

    def _build_columns(self):
        """Bouw kolommen vanuit ViewModel"""
        model = self._vm.model
        columns = model.column_names()

        self.setColumnCount(len(columns))
        self.setHorizontalHeaderLabels(columns)

        # Set column widths
        for i, col_name in enumerate(columns):
            spec = model.get_column_spec(col_name)
            if spec and spec.width > 0:
                self.horizontalHeader().setSectionResizeMode(i, QHeaderView.Fixed)
                self.setColumnWidth(i, spec.width)

    def _connect_signals(self):
        """Connect ViewModel signals"""
        self._vm.data_changed.connect(self.refresh)
        self._vm.error_occurred.connect(self._show_error)

    # ========== Data Binding ==========

    def refresh(self):
        """Refresh table vanuit model"""
        self.setSortingEnabled(False)

        model = self._vm.model
        new_count = model.row_count()

        # Adjust rows
        while self.rowCount() < new_count:
            self.insertRow(self.rowCount())
        while self.rowCount() > new_count:
            self.removeRow(self.rowCount() - 1)

        # Update cells
        columns = model.column_names()
        for row in range(new_count):
            for col_idx, col_name in enumerate(columns):
                value = model.get_cell(row, col_name)
                self._set_cell_value(row, col_idx, col_name, value)

        self.setSortingEnabled(True)

    def _set_cell_value(self, row: int, col: int, col_name: str, value):
        """Set cell met juiste formatting"""
        model = self._vm.model
        spec = model.get_column_spec(col_name)

        # Formatteer voor display
        if spec and spec.formatter and value is not None:
            display_text = spec.formatter(value)
        else:
            display_text = str(value) if value is not None else ""

        # Maak of update item
        item = self.item(row, col)
        if item is None:
            item = QTableWidgetItem(display_text)
            self.setItem(row, col, item)
        else:
            item.setText(display_text)

        # Data role voor sorting
        item.setData(Qt.UserRole, value)

        # Alignment
        if spec and spec.data_type in (int, float):
            item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        else:
            item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)

    # ========== Editing ==========

    def _on_cell_changed(self, row: int, column: int):
        """User heeft cell gewijzigd"""
        if row < 0 or column < 0:
            return

        item = self.item(row, column)
        if not item:
            return

        col_name = self.horizontalHeaderItem(column).text()
        text = item.text()

        # Parse value
        model = self._vm.model
        spec = model.get_column_spec(col_name)

        try:
            if spec and spec.parser:
                value = spec.parser(text)
            elif spec and spec.data_type == int:
                value = int(text)
            elif spec and spec.data_type == float:
                value = float(text)
            else:
                value = text

            # Update via ViewModel
            if not self._vm.update_cell(row, col_name, value):
                # Revert bij falen
                self._revert_cell(row, column, col_name)

        except (ValueError, TypeError):
            self._revert_cell(row, column, col_name)

    def _revert_cell(self, row: int, col: int, col_name: str):
        """Herstel cell naar model waarde"""
        value = self._vm.model.get_cell(row, col_name)
        spec = self._vm.model.get_column_spec(col_name)

        if spec and spec.formatter and value is not None:
            text = spec.formatter(value)
        else:
            text = str(value) if value is not None else ""

        item = self.item(row, col)
        if item:
            item.setText(text)

    # ========== Context Menu ==========

    def _show_context_menu(self, position: QPoint):
        menu = QMenu(self)

        # Add/Insert
        if self._enable_add:
            menu.addAction("Add Row", self._on_add_row)
            menu.addAction("Insert Row", self._on_insert_row)
            menu.addSeparator()

        # Delete
        selected = self._get_selected_rows()
        if selected and self._enable_delete:
            menu.addAction(f"Delete {len(selected)} Row(s)", self._on_delete_rows)
            menu.addSeparator()

        # Batch
        if self._enable_batch and len(selected) > 0:
            current_col = self.currentColumn()
            if current_col >= 0:
                col_name = self.horizontalHeaderItem(current_col).text()
                spec = self._vm.model.get_column_spec(col_name)
                if spec and spec.data_type in (int, float):
                    menu.addAction(
                        f"Offset {col_name}...",
                        lambda: self._on_offset(col_name, selected),
                    )
                    menu.addSeparator()

        # Sort
        if self._enable_sort:
            menu.addAction("Sort", self._on_sort)

        menu.exec_(self.viewport().mapToGlobal(position))

    def _get_selected_rows(self) -> List[int]:
        """Return geselecteerde row indices"""
        rows = set()
        for item in self.selectedItems():
            rows.add(item.row())
        return sorted(rows)

    # ========== Actions ==========

    def _on_add_row(self):
        self._vm.add_row()

    def _on_insert_row(self):
        current = self.currentRow()
        if current < 0:
            current = 0
        self._vm.insert_row(current)

    def _on_delete_rows(self):
        rows = self._get_selected_rows()
        if rows:
            self._vm.delete_rows(rows)

    def _on_offset(self, column: str, rows: List[int]):
        """Toon offset dialog (placeholder)"""
        # In echte implementatie: dialog openen
        # Nu: hardcoded +10
        self._vm.apply_offset(column, rows, 10.0)

    def _on_sort(self):
        current = self.currentColumn()
        if current >= 0:
            col_name = self.horizontalHeaderItem(current).text()
            self._vm.sort(col_name)

    def _show_error(self, message: str):
        QMessageBox.warning(self, "Error", message)
