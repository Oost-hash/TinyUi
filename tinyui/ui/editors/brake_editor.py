#  TinyPedal is an open-source overlay application for racing simulation.
#  Copyright (C) 2022-2026 TinyPedal developers, see contributors.md file
#
#  This file is part of TinyPedal.
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
Brake editor
"""

import logging

from PySide2.QtWidgets import (
    QTableWidgetItem,
    QVBoxLayout,
)

from tinyui.backend.controls import api
from tinyui.backend.constants import ConfigType
from tinyui.backend.settings import cfg, copy_setting
from tinyui.backend.data import HEATMAP_DEFAULT_BRAKE, set_predefined_brake_name
from .._common import UIScaler
from ..components.combo_selector import combo_selector
from ..components.table_items import FloatTableItem
from ._editor_common import TableEditor, editor_button_bar
from ..components.data_table import DataTable

HEADER_BRAKES = "Brake name","Failure (mm)","Heatmap name"

logger = logging.getLogger(__name__)


class BrakeEditor(TableEditor):
    """Brake editor"""

    def __init__(self, parent):
        super().__init__(parent)
        self.set_utility_title("Brake Editor")
        self.setMinimumSize(UIScaler.size(45), UIScaler.size(38))

        self.brakes_temp = copy_setting(cfg.user.brakes)

        # Set table
        self.table = DataTable(
            self, HEADER_BRAKES, column_widths={1: 8, 2: 12}
        )
        self.table.cellChanged.connect(self.verify_input)
        self.refresh_table()
        self.set_unmodified()

        # Set button
        layout_button = editor_button_bar(self, [
            ("Add", self.add_brake),
            ("Sort", self.sort_rows),
            ("Delete", self.delete_rows),
            ("Reset", self.reset_setting),
        ])

        # Set layout
        layout_main = QVBoxLayout()
        layout_main.addWidget(self.table)
        layout_main.addLayout(layout_button)
        layout_main.setContentsMargins(self.MARGIN, self.MARGIN, self.MARGIN, self.MARGIN)
        self.setLayout(layout_main)

    def refresh_table(self):
        """Refresh brakes list"""
        self.table.clear_rows()
        for row_index, (class_name, brake_data) in enumerate(self.brakes_temp.items()):
            self.add_brake_entry(
                row_index,
                class_name,
                brake_data["failure_thickness"],
                brake_data["heatmap"],
            )

    def add_brake(self):
        """Add new brake"""
        start_index = row_index = self.table.rowCount()
        # Add all missing vehicle name from active session
        veh_total = api.read.vehicle.total_vehicles()
        for index in range(veh_total):
            class_name = api.read.vehicle.class_name(index)
            vehicle_name = api.read.vehicle.vehicle_name(index)
            brake_names = (
                set_predefined_brake_name(class_name, vehicle_name, True),
                set_predefined_brake_name(class_name, vehicle_name, False),
            )
            for brake in brake_names:
                if not self.is_value_in_table(brake, self.table):
                    self.add_brake_entry(row_index, brake, 0)
                    self.table.setCurrentCell(row_index, 0)
                    row_index += 1
        # Add new name entry
        if start_index == row_index:
            new_class_name = self.new_name_increment("New Brake Name", self.table)
            self.add_brake_entry(row_index, new_class_name, 0)
            self.table.setCurrentCell(row_index, 0)

    def add_brake_entry(
        self, row_index: int, class_name: str, failure_thickness: float,
        heatmap_name: str = HEATMAP_DEFAULT_BRAKE):
        """Add new brake entry to table"""
        self.table.insert_row(row_index, [
            QTableWidgetItem(class_name),
            FloatTableItem(failure_thickness),
            combo_selector(cfg.user.heatmap.keys(), heatmap_name, self.set_modified),
        ])

    def reset_setting(self):
        """Reset setting"""
        msg_text = (
            "Reset <b>brakes preset</b> to default?<br><br>"
            "Changes are only saved after clicking Apply or Save Button."
        )
        if self.confirm_operation(message=msg_text):
            self.brakes_temp = copy_setting(cfg.default.brakes)
            self.set_modified()
            self.refresh_table()

    def verify_input(self, row_index: int, column_index: int):
        """Verify input value"""
        self.set_modified()
        item = self.table.item(row_index, column_index)
        if column_index == 1:  # failure thickness column
            item.validate()

    def update_temp(self):
        """Update temporary changes to brakes temp"""
        self.brakes_temp.clear()
        for index in range(self.table.rowCount()):
            class_name = self.table.item(index, 0).text()
            failure_thickness = self.table.item(index, 1).value()
            heatmap_name = self.table.cellWidget(index, 2).currentText()
            self.brakes_temp[class_name] = {
                "failure_thickness": failure_thickness,
                "heatmap": heatmap_name,
            }

    def persist(self):
        """Persist brakes to config"""
        cfg.user.brakes = copy_setting(self.brakes_temp)
        cfg.save(0, cfg_type=ConfigType.BRAKES)
