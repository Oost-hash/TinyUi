"""Generic dict-based table editor."""

from __future__ import annotations

import time
from typing import Any

from PySide2.QtCore import Qt
from PySide2.QtWidgets import (
    QTableWidgetItem,
    QVBoxLayout,
)

from tinyui.backend.settings import cfg, copy_setting
from ._base_editor import TableEditor, editor_button_bar
from .._common import UIScaler
from ..components.data_table import DataTable


class GenericDictTableEditor(TableEditor):
    """Generic editor for dict-based table data.

    Covers: brake, tyre compound, vehicle class, vehicle brand, track info.

    Subclasses MUST define class attributes:
        _cfg_attr: str          # "brakes", "compounds", "classes", "brands", "tracks"
        _cfg_type: Any          # ConfigType.BRAKES, etc.
        _title: str             # Window title
        _columns: tuple         # Column headers
        _column_widths: dict    # Optional: {1: 8, 2: 12}
        _min_size: tuple        # Optional: (width, height) in UIScaler units, default (45, 38)

    Subclasses MUST override:
        _row_to_widgets(key, data) -> list  # Convert dict to table row widgets
        _row_to_dict(row_idx: int) -> dict  # Extract dict from table row

    Subclasses CAN override:
        add_row()               # For custom "Add" behavior (API import, etc.)
        _default_row_data()     # Return default values for new row
        verify_input(row, col)  # For custom validation
    """

    _cfg_attr: str = ""
    _cfg_type = None
    _title: str = ""
    _columns: tuple = ()
    _column_widths: dict = None
    _min_size: tuple = (45, 38)

    def __init__(self, parent):
        super().__init__(parent)
        self.set_utility_title(self._title)
        self.setMinimumSize(
            UIScaler.size(self._min_size[0]),
            UIScaler.size(self._min_size[1])
        )

        # Load data from cfg
        self._data_temp = copy_setting(getattr(cfg.user, self._cfg_attr))

        # Setup table
        self.table = DataTable(
            self,
            self._columns,
            column_widths=self._column_widths or {}
        )
        self.table.cellChanged.connect(self.verify_input)

        # Initial refresh
        self.refresh_table()
        self.set_unmodified()

        # Button bar
        layout_button = editor_button_bar(self, [
            ("Add", self.add_row),
            ("Sort", self.sort_rows),
            ("Delete", self.delete_rows),
            ("Reset", self.reset_setting),
        ])

        # Layout
        layout_main = QVBoxLayout()
        layout_main.addWidget(self.table)
        layout_main.addLayout(layout_button)
        layout_main.setContentsMargins(self.MARGIN, self.MARGIN, self.MARGIN, self.MARGIN)
        self.setLayout(layout_main)

    def refresh_table(self):
        """Refresh table from _data_temp."""
        self.table.clear_rows()
        for row_idx, (key, data) in enumerate(self._data_temp.items()):
            widgets = self._row_to_widgets(key, data)
            self.table.insert_row(row_idx, widgets)

    def update_temp(self):
        """Update _data_temp from table."""
        self._data_temp.clear()
        for row_idx in range(self.table.rowCount()):
            key = self.table.item(row_idx, 0).text()
            self._data_temp[key] = self._row_to_dict(row_idx)

    def persist(self):
        """Persist to cfg."""
        setattr(cfg.user, self._cfg_attr, copy_setting(self._data_temp))
        cfg.save(0, cfg_type=self._cfg_type)
        while cfg.is_saving:
            time.sleep(0.01)

    def reset_setting(self):
        """Reset to defaults."""
        msg_text = (
            f"Reset <b>{self._cfg_attr}</b> preset to default?<br><br>"
            "Changes are only saved after clicking Apply or Save Button."
        )
        if self.confirm_operation(message=msg_text):
            self._data_temp = copy_setting(getattr(cfg.default, self._cfg_attr))
            self.set_modified()
            self.refresh_table()

    def verify_input(self, row_index: int, column_index: int):
        """Default: validate on column > 0."""
        self.set_modified()
        if column_index >= 1:
            item = self.table.item(row_index, column_index)
            if hasattr(item, 'validate'):
                item.validate()

    def add_row(self):
        """Default: add 'New X Name' entry. Override for custom behavior."""
        row_idx = self.table.rowCount()
        type_name = self._title.replace(" Editor", "")
        new_name = self.new_name_increment(f"New {type_name} Name", self.table)
        default_data = self._default_row_data()
        widgets = self._row_to_widgets(new_name, default_data)
        self.table.insert_row(row_idx, widgets)
        self.table.setCurrentCell(row_idx, 0)
        self.set_modified()

    def _default_row_data(self) -> dict:
        """Return default data for new row. Override if needed."""
        return {}

    # --- ABSTRACT METHODS ---

    def _row_to_widgets(self, key: str, data: dict) -> list:
        """Convert dict entry to list of table widgets. MUST override."""
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement _row_to_widgets()"
        )

    def _row_to_dict(self, row_idx: int) -> dict:
        """Extract dict from table row. MUST override."""
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement _row_to_dict()"
        )
