#
#  TinyUi - Base Editor View
#  Copyright (C) 2026 Oost-hash
#

from abc import abstractmethod
from typing import Any, Callable, Generic, List, Optional, TypeVar

from PySide2.QtCore import Qt
from PySide2.QtWidgets import (
    QHBoxLayout,
    QMessageBox,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ..core.base_viewmodel import BaseViewModel
from .compact_button import CompactButton
from .data_table import DataTable

T = TypeVar("T")


class BaseEditorView(QWidget, Generic[T]):
    """
    Abstract base for all editor views.
    Provides common UI structure while allowing customization.
    """

    def __init__(
        self, headers: List[str], column_widths: Optional[dict] = None, parent=None
    ):
        super().__init__(parent)
        self._vm: Optional[BaseViewModel[T]] = None
        self._headers = headers
        self._column_widths = column_widths or {}
        self._setup_ui()

    def _setup_ui(self):
        """Create common UI structure."""
        # Table
        self._table = DataTable(
            parent=self, headers=self._headers, column_widths=self._column_widths
        )

        # Standard buttons
        self._btn_add = CompactButton("Add")
        self._btn_import = CompactButton("Import from API")
        self._btn_save = CompactButton("Save")
        self._btn_save.setEnabled(False)

        # Button layout
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self._btn_add)
        btn_layout.addWidget(self._btn_import)
        btn_layout.addStretch()
        btn_layout.addWidget(self._btn_save)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self._table)
        main_layout.addLayout(btn_layout)
        self.setLayout(main_layout)

        # Connect common signals
        self._btn_add.clicked.connect(self._on_add_clicked)
        self._btn_import.clicked.connect(self._on_import_clicked)
        self._btn_save.clicked.connect(self._on_save_clicked)

    def bind_to(self, vm: BaseViewModel[T]):
        """Bind to viewmodel - connects all standard signals."""
        self._vm = vm

        # VM signals -> View updates
        vm.data_changed.connect(self._refresh_table)
        vm.modified_changed.connect(self._on_modified_changed)
        vm.error_occurred.connect(self._show_error)
        vm.operation_completed.connect(self._show_success)

        # Load initial data
        if vm.load():
            self._refresh_table()

    @abstractmethod
    def _refresh_table(self):
        """
        Populate table with data from VM.
        Override to add custom widgets (dropdowns, etc.).
        """
        pass

    @abstractmethod
    def _on_add_clicked(self):
        """Handle Add button. Override for custom logic."""
        pass

    def _on_import_clicked(self):
        """Handle Import button - default delegates to VM."""
        if self._vm and hasattr(self._vm, "import_from_api"):
            self._vm.import_from_api()

    def _on_save_clicked(self):
        """Handle Save button - default delegates to VM."""
        if self._vm:
            self._vm.save()

    def _on_modified_changed(self, is_modified: bool):
        """Update save button state."""
        self._btn_save.setEnabled(is_modified)

    def _show_error(self, message: str):
        """Show error dialog."""
        QMessageBox.critical(self, "Error", message)

    def _show_success(self, message: str):
        """Show success dialog."""
        QMessageBox.information(self, "Success", message)

    # Utility methods for subclasses

    def _get_selected_key(self) -> Optional[str]:
        """Get key of currently selected row."""
        row = self._table.currentRow()
        if row >= 0:
            return self._table.get_row_key(row)
        return None

    def _set_cell_widget(self, row: int, col: int, widget: QWidget):
        """Set custom widget in table cell."""
        self._table.setCellWidget(row, col, widget)

    def _refresh_cell(self, row: int, col: int, value: Any):
        """Update single cell value."""
        self._table.set_cell_value(row, col, value)
