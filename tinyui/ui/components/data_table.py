"""Reusable data table component."""

from PySide2.QtCore import Signal
from PySide2.QtWidgets import (
    QHeaderView,
    QTableWidget,
    QTableWidgetItem,
    QWidget,
)

from .. import UIScaler


class DataTable(QTableWidget):
    """Table component with row management and typed cells.

    Signals:
        rowCountChanged: emitted when rows are added or removed.
    """

    rowCountChanged = Signal(int)

    def __init__(self, parent: QWidget = None, headers: tuple = (),
                 column_widths: dict = None, show_row_header: bool = True):
        super().__init__(parent)
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)
        self.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        if not show_row_header:
            self.verticalHeader().setVisible(False)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        if column_widths:
            for col, width in column_widths.items():
                self.horizontalHeader().setSectionResizeMode(col, QHeaderView.Fixed)
                self.setColumnWidth(col, UIScaler.size(width))

    # ---- Row management ----

    def add_row(self, items: list) -> int:
        """Append a row with items. Returns the new row index.

        items: list of QTableWidgetItem or QWidget (cell widgets).
        """
        row = self.rowCount()
        self.insertRow(row)
        self._set_row(row, items)
        self.rowCountChanged.emit(self.rowCount())
        return row

    def insert_row(self, row: int, items: list) -> int:
        """Insert a row at position with items. Returns the row index."""
        row = max(0, min(row, self.rowCount()))
        self.insertRow(row)
        self._set_row(row, items)
        self.rowCountChanged.emit(self.rowCount())
        return row

    def delete_selected_rows(self) -> list[int]:
        """Delete all selected rows. Returns list of deleted row indices."""
        rows = sorted(set(idx.row() for idx in self.selectedIndexes()), reverse=True)
        for row in rows:
            self.removeRow(row)
        if rows:
            self.rowCountChanged.emit(self.rowCount())
        return rows

    def sort_by_column(self, column: int = 0):
        """Sort rows by column."""
        if self.rowCount() > 1:
            self.sortItems(column)

    def clear_rows(self):
        """Remove all rows, keep headers."""
        self.setRowCount(0)
        self.rowCountChanged.emit(0)

    # ---- Helpers ----

    def selected_rows(self) -> set[int]:
        """Get set of selected row indices."""
        return set(idx.row() for idx in self.selectedIndexes())

    def selected_column_count(self, column: int) -> int:
        """Count selected cells in a specific column.
        Returns 0 if any selection is outside the column.
        """
        count = 0
        for idx in self.selectedIndexes():
            if idx.column() == column:
                count += 1
            else:
                return 0
        return count

    def has_value(self, value: str, column: int = 0) -> bool:
        """Check if value exists in column."""
        items = self.findItems(value, 2)  # Qt.MatchExactly = 2
        return any(item.column() == column for item in items)

    def _set_row(self, row: int, items: list):
        """Set items/widgets for a row."""
        for col, item in enumerate(items):
            if isinstance(item, QTableWidgetItem):
                self.setItem(row, col, item)
            elif isinstance(item, QWidget):
                self.setCellWidget(row, col, item)
