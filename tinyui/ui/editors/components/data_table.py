#
#  TinyUi - Data Table Component
#  Copyright (C) 2026 Oost-hash
#

from typing import Any, Callable, Dict, List, Optional, Tuple

from PySide2.QtCore import Qt, Signal
from PySide2.QtWidgets import QAbstractItemView, QTableWidget, QTableWidgetItem, QWidget


class DataTable(QTableWidget):
    """
    Dumb table component - only renders data and emits events.
    No knowledge of data source, validation, or business logic.
    """

    cell_edited = Signal(int, int, str)  # row, col, new_value
    row_selected = Signal(int)  # row index
    context_menu_requested = Signal(int, int)  # row, col

    def __init__(
        self,
        parent=None,
        headers: List[str] = None,
        column_widths: Optional[Dict[int, int]] = None,
        editable_columns: Optional[List[int]] = None,
    ):
        super().__init__(parent)
        self._headers = headers or []
        self._editable_columns = editable_columns or []
        self._cell_widgets: Dict[Tuple[int, int], QWidget] = {}

        self.setColumnCount(len(self._headers))
        self.setHorizontalHeaderLabels(self._headers)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setAlternatingRowColors(True)

        if column_widths:
            for col, width in column_widths.items():
                self.setColumnWidth(col, width)

        self.cellChanged.connect(self._on_cell_changed)
        self.itemSelectionChanged.connect(self._on_selection_changed)

    def bind_data(
        self, data: Dict[str, Any], row_factory: Callable[[str, Any], List[Any]]
    ):
        """
        Populate table from data dict.
        row_factory: function that creates table row from (key, value)
        """
        self.clear_rows()
        for row_idx, (key, value) in enumerate(data.items()):
            row_data = row_factory(key, value)
            self._insert_row(row_idx, key, row_data)

    def _insert_row(self, row_idx: int, key: str, row_data: List[Any]):
        """Insert a row with mixed item types."""
        self.insertRow(row_idx)
        self.setVerticalHeaderItem(row_idx, QTableWidgetItem(str(row_idx)))

        for col_idx, cell_data in enumerate(row_data):
            if isinstance(cell_data, QWidget):
                # Custom widget (combo, color picker, etc.)
                self.setCellWidget(row_idx, col_idx, cell_data)
                self._cell_widgets[(row_idx, col_idx)] = cell_data
            elif isinstance(cell_data, QTableWidgetItem):
                # Pre-configured item
                self.setItem(row_idx, col_idx, cell_data)
            else:
                # Plain text
                item = QTableWidgetItem(str(cell_data))
                item.setData(Qt.UserRole, key)  # Store key for reference
                if col_idx not in self._editable_columns:
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.setItem(row_idx, col_idx, item)

    def _on_cell_changed(self, row: int, col: int):
        """Emit edit event - don't handle logic here."""
        item = self.item(row, col)
        if item:
            self.cell_edited.emit(row, col, item.text())

    def _on_selection_changed(self):
        """Emit selection event."""
        selected = self.selectedIndexes()
        if selected:
            self.row_selected.emit(selected[0].row())

    def get_row_key(self, row: int) -> Optional[str]:
        """Get the data key for a row."""
        item = self.item(row, 0)
        if item:
            return item.data(Qt.UserRole)
        return None

    def get_cell_value(self, row: int, col: int) -> Any:
        """Get value from cell widget or item."""
        # Check for custom widget first
        widget = self._cell_widgets.get((row, col))
        if widget:
            # Widget must implement get_value()
            if hasattr(widget, "get_value"):
                return widget.get_value()
            elif hasattr(widget, "currentText"):  # QComboBox
                return widget.currentText()
            elif hasattr(widget, "text"):  # QLineEdit
                return widget.text()

        # Regular table item
        item = self.item(row, col)
        return item.text() if item else None

    def set_cell_value(self, row: int, col: int, value: Any):
        """Update cell without triggering edit signal."""
        self.blockSignals(True)

        widget = self._cell_widgets.get((row, col))
        if widget:
            if hasattr(widget, "set_value"):
                widget.set_value(value)
            elif hasattr(widget, "setCurrentText"):
                widget.setCurrentText(str(value))
            elif hasattr(widget, "setText"):
                widget.setText(str(value))
        else:
            item = self.item(row, col)
            if item:
                item.setText(str(value))

        self.blockSignals(False)

    def clear_rows(self):
        """Remove all rows."""
        self.setRowCount(0)
        self._cell_widgets.clear()

    def refresh_cell(self, row: int, col: int, value: Any):
        """Update single cell from external source."""
        self.set_cell_value(row, col, value)
