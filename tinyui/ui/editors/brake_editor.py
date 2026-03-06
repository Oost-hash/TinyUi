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
import time

from PySide2.QtWidgets import (
    QComboBox,
    QMessageBox,
    QTableWidgetItem,
    QVBoxLayout,
)

from tinypedal.api_control import api
from tinypedal.const_file import ConfigType
from tinypedal.setting import cfg, copy_setting
from tinypedal.userfile.heatmap import HEATMAP_DEFAULT_BRAKE, set_predefined_brake_name
from .._common import (
    BaseEditor,
    FloatTableItem,
    UIScaler,
    editor_button_bar,
    setup_table,
)

HEADER_BRAKES = "Brake name","Failure (mm)","Heatmap name"

logger = logging.getLogger(__name__)


class BrakeEditor(BaseEditor):
    """Brake editor"""

    def __init__(self, parent):
        super().__init__(parent)
        self.set_utility_title("Brake Editor")
        self.setMinimumSize(UIScaler.size(45), UIScaler.size(38))

        self.brakes_temp = copy_setting(cfg.user.brakes)

        # Set table
        self.table_brakes = setup_table(
            self, HEADER_BRAKES, column_widths={1: 8, 2: 12}
        )
        self.table_brakes.cellChanged.connect(self.verify_input)
        self.refresh_table()
        self.set_unmodified()

        # Set button
        layout_button = self.set_layout_button()

        # Set layout
        layout_main = QVBoxLayout()
        layout_main.addWidget(self.table_brakes)
        layout_main.addLayout(layout_button)
        layout_main.setContentsMargins(self.MARGIN, self.MARGIN, self.MARGIN, self.MARGIN)
        self.setLayout(layout_main)

    def set_layout_button(self):
        """Set button layout"""
        return editor_button_bar(self, [
            ("Add", self.add_brake),
            ("Sort", self.sort_brake),
            ("Delete", self.delete_brake),
            ("Reset", self.reset_setting),
        ])

    def refresh_table(self):
        """Refresh brakes list"""
        self.table_brakes.setRowCount(0)
        row_index = 0
        for class_name, brake_data in self.brakes_temp.items():
            self.add_brake_entry(
                row_index,
                class_name,
                brake_data["failure_thickness"],
                brake_data["heatmap"],
            )
            row_index += 1

    def __add_option_combolist(self, key):
        """Combo droplist string"""
        combo_edit = QComboBox()
        combo_edit.addItems(cfg.user.heatmap.keys())
        combo_edit.setCurrentText(key)
        combo_edit.currentTextChanged.connect(self.set_modified)
        return combo_edit

    #def open_replace_dialog(self):
    #    """Open replace dialog"""
    #    selector = {HEADER_BRAKES[0]: 0}
    #    _dialog = TableBatchReplace(self, selector, self.table_brakes)
    #    _dialog.open()

    def add_brake(self):
        """Add new brake"""
        start_index = row_index = self.table_brakes.rowCount()
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
                if not self.is_value_in_table(brake, self.table_brakes):
                    self.add_brake_entry(row_index, brake, 0)
                    self.table_brakes.setCurrentCell(row_index, 0)
                    row_index += 1
        # Add new name entry
        if start_index == row_index:
            new_class_name = self.new_name_increment("New Brake Name", self.table_brakes)
            self.add_brake_entry(row_index, new_class_name, 0)
            self.table_brakes.setCurrentCell(row_index, 0)

    def add_brake_entry(
        self, row_index: int, class_name: str, failure_thickness: float,
        heatmap_name: str = HEATMAP_DEFAULT_BRAKE):
        """Add new brake entry to table"""
        self.table_brakes.insertRow(row_index)
        self.table_brakes.setItem(row_index, 0, QTableWidgetItem(class_name))
        self.table_brakes.setItem(row_index, 1, FloatTableItem(failure_thickness))
        self.table_brakes.setCellWidget(row_index, 2, self.__add_option_combolist(heatmap_name))

    def sort_brake(self):
        """Sort brakes in ascending order"""
        if self.table_brakes.rowCount() > 1:
            self.table_brakes.sortItems(0)
            self.set_modified()

    def delete_brake(self):
        """Delete brake entry"""
        selected_rows = set(data.row() for data in self.table_brakes.selectedIndexes())
        if not selected_rows:
            QMessageBox.warning(self, "Error", "No data selected.")
            return

        if not self.confirm_operation(message="<b>Delete selected rows?</b>"):
            return

        for row_index in sorted(selected_rows, reverse=True):
            self.table_brakes.removeRow(row_index)
        self.set_modified()

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

    def applying(self):
        """Save & apply"""
        self.save_setting()

    def saving(self):
        """Save & close"""
        self.save_setting()
        self.accept()  # close

    def verify_input(self, row_index: int, column_index: int):
        """Verify input value"""
        self.set_modified()
        item = self.table_brakes.item(row_index, column_index)
        if column_index == 1:  # failure thickness column
            item.validate()

    def update_brakes_temp(self):
        """Update temporary changes to brakes temp first"""
        self.brakes_temp.clear()
        for index in range(self.table_brakes.rowCount()):
            class_name = self.table_brakes.item(index, 0).text()
            failure_thickness = self.table_brakes.item(index, 1).value()
            heatmap_name = self.table_brakes.cellWidget(index, 2).currentText()
            self.brakes_temp[class_name] = {
                "failure_thickness": failure_thickness,
                "heatmap": heatmap_name,
            }

    def save_setting(self):
        """Save setting"""
        self.update_brakes_temp()
        cfg.user.brakes = copy_setting(self.brakes_temp)
        cfg.save(0, cfg_type=ConfigType.BRAKES)
        while cfg.is_saving:  # wait saving finish
            time.sleep(0.01)
        self.reloading()
        self.set_unmodified()
