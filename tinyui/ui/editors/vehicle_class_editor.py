"""Vehicle class editor - refactored to use GenericDictTableEditor."""

import random

from PySide2.QtWidgets import QTableWidgetItem

from tinyui.backend.constants import EMPTY_DICT, ConfigType
from tinyui.backend.controls import api
from tinyui.backend.formatter import random_color_class
from tinyui.backend.settings import cfg

from .._common import QVAL_COLOR
from .._option import ColorEdit
from ._generic_dict_editor import GenericDictTableEditor


class VehicleClassEditor(GenericDictTableEditor):
    """Vehicle class editor."""

    _cfg_attr = "classes"
    _cfg_type = ConfigType.CLASSES
    _title = "Vehicle Class Editor"
    _columns = ("Class name", "Alias name", "Color")
    _column_widths = {2: 7}
    _min_size = (30, 30)

    def _create_color_edit(self, color: str) -> ColorEdit:
        """Create color editor widget."""
        color_edit = ColorEdit(self, color)
        color_edit.setMaxLength(9)
        color_edit.setValidator(QVAL_COLOR)
        color_edit.textChanged.connect(self.set_modified)
        color_edit.setText(color)
        return color_edit

    def _row_to_widgets(self, key: str, data: dict) -> list:
        """Convert class data to table row."""
        return [
            QTableWidgetItem(key),
            QTableWidgetItem(data.get("alias", key)),
            self._create_color_edit(data.get("color", "#FFFFFF")),
        ]

    def _row_to_dict(self, row_idx: int) -> dict:
        """Extract class data from table row."""
        # Preserve existing preset if any
        key = self.table.item(row_idx, 0).text()
        existing = getattr(cfg.user, self._cfg_attr).get(key, EMPTY_DICT)

        return {
            "alias": self.table.item(row_idx, 1).text(),
            "color": self.table.cellWidget(row_idx, 2).text(),
            "preset": existing.get("preset", ""),
        }

    def add_row(self):
        """Add new class - auto-import from API or create new."""
        start_idx = row_idx = self.table.rowCount()

        # Try auto-import from active session
        veh_total = api.read.vehicle.total_vehicles()
        for idx in range(veh_total):
            class_name = api.read.vehicle.class_name(idx)
            if not self.is_value_in_table(class_name, self.table):
                widgets = self._row_to_widgets(
                    class_name,
                    {"alias": class_name, "color": random_color_class(class_name)},
                )
                self.table.insert_row(row_idx, widgets)
                row_idx += 1

        # Add new entry if no API data
        if start_idx == row_idx:
            row_idx = self.table.rowCount()
            new_name = self.new_name_increment("New Class Name", self.table)
            widgets = self._row_to_widgets(
                new_name,
                {"alias": "NAME", "color": random_color_class(str(random.random()))},
            )
            self.table.insert_row(row_idx, widgets)
            self.table.setCurrentCell(row_idx, 0)
            self.set_modified()
