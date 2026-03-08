"""Brake editor - refactored to use GenericDictTableEditor."""

from PySide2.QtWidgets import QTableWidgetItem

from tinyui.backend.constants import ConfigType
from tinyui.backend.controls import api
from tinyui.backend.data import HEATMAP_DEFAULT_BRAKE, set_predefined_brake_name
from tinyui.backend.settings import cfg

from ..components.combo_selector import combo_selector
from ..components.table_items import FloatTableItem
from ._generic_dict_editor import GenericDictTableEditor


class BrakeEditor(GenericDictTableEditor):
    """Brake editor."""

    _cfg_attr = "brakes"
    _cfg_type = ConfigType.BRAKES
    _title = "Brake Editor"
    _columns = ("Brake name", "Failure (mm)", "Heatmap name")
    _column_widths = {1: 8, 2: 12}
    _min_size = (45, 38)

    def _row_to_widgets(self, key: str, data: dict) -> list:
        """Convert brake data to table row."""
        return [
            QTableWidgetItem(key),
            FloatTableItem(data.get("failure_thickness", 0)),
            combo_selector(
                cfg.user.heatmap.keys(),
                data.get("heatmap", HEATMAP_DEFAULT_BRAKE),
                self.set_modified,
            ),
        ]

    def _row_to_dict(self, row_idx: int) -> dict:
        """Extract brake data from table row."""
        return {
            "failure_thickness": self.table.item(row_idx, 1).value(),
            "heatmap": self.table.cellWidget(row_idx, 2).currentText(),
        }

    def add_row(self):
        """Add new brake - auto-import from API or create new."""
        start_idx = row_idx = self.table.rowCount()

        # Try auto-import from active session
        veh_total = api.read.vehicle.total_vehicles()
        for idx in range(veh_total):
            class_name = api.read.vehicle.class_name(idx)
            vehicle_name = api.read.vehicle.vehicle_name(idx)
            brake_names = (
                set_predefined_brake_name(class_name, vehicle_name, True),
                set_predefined_brake_name(class_name, vehicle_name, False),
            )
            for brake in brake_names:
                if not self.is_value_in_table(brake, self.table):
                    widgets = self._row_to_widgets(
                        brake,
                        {"failure_thickness": 0, "heatmap": HEATMAP_DEFAULT_BRAKE},
                    )
                    self.table.insert_row(row_idx, widgets)
                    self.table.setCurrentCell(row_idx, 0)
                    row_idx += 1

        # Add new entry if no API data
        if start_idx == row_idx:
            super().add_row()
        else:
            self.set_modified()
