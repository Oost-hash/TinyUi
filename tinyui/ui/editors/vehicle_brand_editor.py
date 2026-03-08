"""Vehicle brand editor - refactored to use GenericDictTableEditor."""

import asyncio
import json
import logging
import os

from PySide2.QtWidgets import (
    QMenu,
    QMessageBox,
    QTableWidgetItem,
)

from tinyui.backend.constants import (
    API_LMU_ALIAS,
    API_LMU_CONFIG,
    API_RF2_ALIAS,
    API_RF2_CONFIG,
    ConfigType,
    FileFilter,
)
from tinyui.backend.controls import api
from tinyui.backend.formatter import strip_invalid_char
from tinyui.backend.misc import get_response, set_header_get
from tinyui.backend.settings import cfg

from .._common import UIScaler
from ..components.compact_button import CompactButton
from ..components.data_table import DataTable
from ._base_editor import TableEditor, editor_button_bar
from ._generic_dict_editor import GenericDictTableEditor

logger = logging.getLogger(__name__)


class VehicleBrandEditor(GenericDictTableEditor):
    """Vehicle brand editor."""

    _cfg_attr = "brands"
    _cfg_type = ConfigType.BRANDS
    _title = "Vehicle Brand Editor"
    _columns = ("Vehicle name", "Brand name")
    _min_size = (45, 38)

    def __init__(self, parent):
        super().__init__(parent)
        # Replace default button bar with import button
        self._setup_import_button()

    def _setup_import_button(self):
        """Setup button bar with import menu."""
        # Clear existing layout and rebuild with import button
        # Note: This is a bit hacky, ideally GenericDictTableEditor would support custom buttons
        # For now, we override the layout after super().__init__()

        # Import menu button
        import_menu = QMenu(self)
        import_menu.addAction("RF2 Rest API").triggered.connect(self.import_from_rf2)
        import_menu.addAction("LMU Rest API (Primary)").triggered.connect(
            self.import_from_lmu
        )
        import_menu.addAction("LMU Rest API (Alternative)").triggered.connect(
            self.import_from_lmu_alt
        )
        import_menu.addAction("JSON file").triggered.connect(self.import_from_file)

        button_import = CompactButton("Import from", has_menu=True)
        button_import.setMenu(import_menu)

        # Rebuild button bar (simplified version)
        # In practice, you might want to modify GenericDictTableEditor to accept extra buttons
        layout = self.layout()
        # Remove old button layout (last item) and add new one
        old_button_layout = layout.takeAt(layout.count() - 1)

        new_button_layout = editor_button_bar(
            self,
            [
                ("Add", self.add_row),
                ("Sort", lambda: self.sort_rows(1)),
                ("Delete", self.delete_rows),
                ("Replace", self.open_replace_dialog),
                ("Reset", self.reset_setting),
            ],
        )
        # Insert import button at start
        new_button_layout.insertWidget(0, button_import)

        layout.addLayout(new_button_layout)

    def _row_to_widgets(self, key: str, data: str) -> list:
        """Convert brand data to table row."""
        return [
            QTableWidgetItem(key),
            QTableWidgetItem(data),
        ]

    def _row_to_dict(self, row_idx: int) -> str:
        """Extract brand from table row - returns string, not dict."""
        return self.table.item(row_idx, 1).text()

    def add_row(self):
        """Add new brand - auto-import from API or create new."""
        start_idx = row_idx = self.table.rowCount()

        # Try auto-import from active session
        veh_total = api.read.vehicle.total_vehicles()
        for idx in range(veh_total):
            veh_name = api.read.vehicle.vehicle_name(idx)
            if not self.is_value_in_table(veh_name, self.table):
                widgets = self._row_to_widgets(veh_name, "Unknown")
                self.table.insert_row(row_idx, widgets)
                row_idx += 1

        # Add new entry if no API data
        if start_idx == row_idx:
            super().add_row()

    def open_replace_dialog(self):
        """Open replace dialog."""
        from ._editor_common import TableBatchReplace

        selector = {self._columns[1]: 1}
        dialog = TableBatchReplace(self, selector, self.table)
        dialog.open()

    # --- Import methods (unchanged logic, slightly cleaned) ---

    def import_from_rf2(self):
        """Import brand from RF2."""
        setting = cfg.user.setting[API_RF2_CONFIG]
        self._import_from_api(
            API_RF2_ALIAS, setting["url_host"], setting["url_port"], "/rest/race/car"
        )

    def import_from_lmu(self):
        """Import brand from LMU (primary)."""
        setting = cfg.user.setting[API_LMU_CONFIG]
        self._import_from_api(
            API_LMU_ALIAS, setting["url_host"], setting["url_port"], "/rest/race/car"
        )

    def import_from_lmu_alt(self):
        """Import brand from LMU (alternative)."""
        setting = cfg.user.setting[API_LMU_CONFIG]
        self._import_from_api(
            API_LMU_ALIAS,
            setting["url_host"],
            setting["url_port"],
            "/rest/sessions/getAllVehicles",
        )

    def _import_from_api(self, sim_name: str, host: str, port: int, resource: str):
        """Import from REST API."""
        header = set_header_get(resource, host)
        try:
            raw = asyncio.run(get_response(header, host, port, 3))
            self._parse_brand_data(json.loads(raw))
        except Exception:
            logger.error("Failed importing from %s API", sim_name)
            QMessageBox.warning(
                self,
                "Error",
                f"Unable to import from {sim_name} API.<br><br>"
                "Make sure game is running and try again.",
            )

    def import_from_file(self):
        """Import brand from JSON file."""
        from PySide2.QtWidgets import QFileDialog

        filename, _ = QFileDialog.getOpenFileName(self, filter=FileFilter.JSON)
        if not filename:
            return

        try:
            if os.path.getsize(filename) > 5120000:
                raise ValueError("File too large")
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
                self._parse_brand_data(data)
        except Exception:
            logger.error("Failed importing %s", filename)
            QMessageBox.warning(
                self,
                "Error",
                "Cannot import selected file.<br><br>Invalid vehicle data file.",
            )

    def _parse_brand_data(self, vehicles: list):
        """Parse brand data from API response."""
        if not vehicles:
            raise ValueError("Empty vehicle list")

        # Detect format
        if vehicles[0].get("desc"):
            # LMU format
            brands = {v["desc"]: v["manufacturer"] for v in vehicles}
        elif vehicles[0].get("name"):
            # RF2 format
            brands = {_parse_vehicle_name(v): v["manufacturer"] for v in vehicles}
        else:
            raise ValueError("Unknown format")

        # Merge with existing
        self.update_temp()
        brands.update(self._data_temp)
        self._data_temp = brands
        self.refresh_table()
        QMessageBox.information(self, "Data Imported", "Vehicle brand data imported.")


def _parse_vehicle_name(vehicle: dict) -> str:
    """Parse vehicle name from RF2 path."""
    path = vehicle.get("vehFile", "")
    parts = path.split("\\")

    if len(parts) >= 2:
        # Version from path: "CAR_24.VEH" → "1.50" from parts[-2]
        version_len = len(parts[-2]) + 1
    else:
        # Fallback: version from name
        version_len = len(vehicle["name"].split(" ")[-1]) + 1

    return vehicle["name"][:-version_len]
