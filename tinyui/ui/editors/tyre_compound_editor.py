"""Tyre compound editor - refactored to use GenericDictTableEditor."""

from PySide2.QtWidgets import QTableWidgetItem

from tinyui.backend.constants import ConfigType
from tinyui.backend.controls import api
from tinyui.backend.data import HEATMAP_DEFAULT_TYRE, set_predefined_compound_symbol
from tinyui.backend.settings import cfg

from ..components.combo_selector import combo_selector
from ._generic_dict_editor import GenericDictTableEditor


class TyreCompoundEditor(GenericDictTableEditor):
    """Tyre compound editor."""

    _cfg_attr = "compounds"
    _cfg_type = ConfigType.COMPOUNDS
    _title = "Tyre Compound Editor"
    _columns = ("Compound name", "Symbol", "Heatmap name")
    _column_widths = {1: 6, 2: 12}
    _min_size = (45, 38)

    def _row_to_widgets(self, key: str, data: dict) -> list:
        """Convert compound data to table row."""
        return [
            QTableWidgetItem(key),
            QTableWidgetItem(data.get("symbol", "?")),
            combo_selector(
                cfg.user.heatmap.keys(),
                data.get("heatmap", HEATMAP_DEFAULT_TYRE),
                self.set_modified,
            ),
        ]

    def _row_to_dict(self, row_idx: int) -> dict:
        """Extract compound data from table row."""
        return {
            "symbol": self.table.item(row_idx, 1).text(),
            "heatmap": self.table.cellWidget(row_idx, 2).currentText(),
        }

    def _default_row_data(self) -> dict:
        """Default data for new compound."""
        return {"symbol": "?", "heatmap": HEATMAP_DEFAULT_TYRE}

    def add_row(self):
        """Add new compound - auto-import from API or create new."""
        start_idx = row_idx = self.table.rowCount()

        # Try auto-import from active session
        veh_total = api.read.vehicle.total_vehicles()
        for idx in range(veh_total):
            class_name = api.read.vehicle.class_name(idx)
            compound_names = {
                f"{class_name} - {api.read.tyre.compound_name_front(idx)}",
                f"{class_name} - {api.read.tyre.compound_name_rear(idx)}",
            }
            for compound in compound_names:
                if not self.is_value_in_table(compound, self.table):
                    widgets = self._row_to_widgets(
                        compound,
                        {
                            "symbol": set_predefined_compound_symbol(compound),
                            "heatmap": HEATMAP_DEFAULT_TYRE,
                        },
                    )
                    self.table.insert_row(row_idx, widgets)
                    self.table.setCurrentCell(row_idx, 0)
                    row_idx += 1

        # Add new entry if no API data
        if start_idx == row_idx:
            super().add_row()
        else:
            self.set_modified()

    def verify_input(self, row_index: int, column_index: int):
        """Custom validation: symbol column limited to 1 char."""
        self.set_modified()
        if column_index == 1:
            item = self.table.item(row_index, column_index)
            text = item.text()
            if not text:
                item.setText("?")
            else:
                item.setText(text[:1])
