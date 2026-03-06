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
Vehicle class editor
"""

import random

from PySide2.QtWidgets import (
    QTableWidgetItem,
    QVBoxLayout,
)

from tinypedal.api_control import api
from tinypedal.const_common import EMPTY_DICT
from tinypedal.const_file import ConfigType
from tinypedal.formatter import random_color_class
from tinypedal.setting import cfg, copy_setting
from .._common import (
    QVAL_COLOR,
    TableEditor,
    UIScaler,
    editor_button_bar,
    setup_table,
)
from .._option import ColorEdit

HEADER_CLASSES = "Class name","Alias name","Color"


class VehicleClassEditor(TableEditor):
    """Vehicle class editor"""

    def __init__(self, parent):
        super().__init__(parent)
        self.set_utility_title("Vehicle Class Editor")
        self.setMinimumSize(UIScaler.size(30), UIScaler.size(30))

        self.classes_temp = copy_setting(cfg.user.classes)

        # Set table
        self.table = setup_table(
            self, HEADER_CLASSES, column_widths={2: 7}, show_row_header=False
        )
        self.table.cellChanged.connect(self.set_modified)
        self.refresh_table()
        self.set_unmodified()

        # Set button
        layout_button = editor_button_bar(self, [
            ("Add", self.add_class),
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
        """Refresh class list"""
        self.table.setRowCount(0)
        row_index = 0
        for class_name, class_data in self.classes_temp.items():
            self.add_vehicle_entry(
                row_index, class_name, class_data["alias"], class_data["color"])
            row_index += 1

    def __add_option_color(self, key):
        """Color string"""
        color_edit = ColorEdit(self, key)
        color_edit.setMaxLength(9)
        color_edit.setValidator(QVAL_COLOR)
        color_edit.textChanged.connect(self.set_modified)
        color_edit.setText(key)  # load selected option
        return color_edit

    def add_class(self):
        """Add new class entry"""
        start_index = row_index = self.table.rowCount()
        # Add all missing vehicle class from active session
        veh_total = api.read.vehicle.total_vehicles()
        for index in range(veh_total):
            class_name = api.read.vehicle.class_name(index)
            if not self.is_value_in_table(class_name, self.table):
                self.add_vehicle_entry(
                    row_index, class_name, class_name, random_color_class(class_name))
                row_index += 1
        # Add new class entry
        if start_index == row_index:
            new_class_name = self.new_name_increment("New Class Name", self.table)
            self.add_vehicle_entry(
                row_index, new_class_name, "NAME", random_color_class(str(random.random())))
            self.table.setCurrentCell(row_index, 0)

    def add_vehicle_entry(self, row_index: int, class_name: str, alias_name: str, color: str):
        """Add new class entry to table"""
        self.table.insertRow(row_index)
        self.table.setItem(row_index, 0, QTableWidgetItem(class_name))
        self.table.setItem(row_index, 1, QTableWidgetItem(alias_name))
        self.table.setCellWidget(row_index, 2, self.__add_option_color(color))

    def reset_setting(self):
        """Reset setting"""
        msg_text = (
            "Reset <b>classes preset</b> to default?<br><br>"
            "Changes are only saved after clicking Apply or Save Button."
        )
        if self.confirm_operation(message=msg_text):
            self.classes_temp = copy_setting(cfg.default.classes)
            self.set_modified()
            self.refresh_table()

    def update_temp(self):
        """Update temporary changes to class temp"""
        loaded = self.classes_temp.copy()
        self.classes_temp.clear()
        for index in range(self.table.rowCount()):
            class_name = self.table.item(index, 0).text()
            abbr_name = self.table.item(index, 1).text()
            color_string = self.table.cellWidget(index, 2).text()
            self.classes_temp[class_name] = {
                "alias": abbr_name,
                "color": color_string,
                "preset": loaded.get(class_name, EMPTY_DICT).get("preset", ""),
            }

    def persist(self):
        """Persist classes to config"""
        cfg.user.classes = copy_setting(self.classes_temp)
        cfg.save(0, cfg_type=ConfigType.CLASSES)
