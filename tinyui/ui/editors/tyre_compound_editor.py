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
Tyre compound editor
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
from tinypedal.userfile.heatmap import HEATMAP_DEFAULT_TYRE, set_predefined_compound_symbol
from .._common import (
    BaseEditor,
    TableBatchReplace,
    UIScaler,
    editor_button_bar,
    setup_table,
)

HEADER_COMPOUNDS = "Compound name","Symbol","Heatmap name"

logger = logging.getLogger(__name__)


class TyreCompoundEditor(BaseEditor):
    """Tyre compound editor"""

    def __init__(self, parent):
        super().__init__(parent)
        self.set_utility_title("Tyre Compound Editor")
        self.setMinimumSize(UIScaler.size(45), UIScaler.size(38))

        self.compounds_temp = copy_setting(cfg.user.compounds)

        # Set table
        self.table_compounds = setup_table(
            self, HEADER_COMPOUNDS, column_widths={1: 6, 2: 12}
        )
        self.table_compounds.cellChanged.connect(self.verify_input)
        self.refresh_table()
        self.set_unmodified()

        # Set button
        layout_button = self.set_layout_button()

        # Set layout
        layout_main = QVBoxLayout()
        layout_main.addWidget(self.table_compounds)
        layout_main.addLayout(layout_button)
        layout_main.setContentsMargins(self.MARGIN, self.MARGIN, self.MARGIN, self.MARGIN)
        self.setLayout(layout_main)

    def set_layout_button(self):
        """Set button layout"""
        return editor_button_bar(self, [
            ("Add", self.add_compound),
            ("Sort", self.sort_compound),
            ("Delete", self.delete_compound),
            ("Replace", self.open_replace_dialog),
            ("Reset", self.reset_setting),
        ])

    def refresh_table(self):
        """Refresh compounds list"""
        self.table_compounds.setRowCount(0)
        row_index = 0
        for compound_name, compound_data in self.compounds_temp.items():
            self.add_compound_entry(
                row_index,
                compound_name,
                compound_data["symbol"],
                compound_data["heatmap"],
            )
            row_index += 1

    def __add_option_combolist(self, key):
        """Combo droplist string"""
        combo_edit = QComboBox()
        combo_edit.addItems(cfg.user.heatmap.keys())
        combo_edit.setCurrentText(key)
        combo_edit.currentTextChanged.connect(self.set_modified)
        return combo_edit

    def open_replace_dialog(self):
        """Open replace dialog"""
        selector = {HEADER_COMPOUNDS[1]: 1}
        _dialog = TableBatchReplace(self, selector, self.table_compounds)
        _dialog.open()

    def add_compound(self):
        """Add new compound"""
        start_index = row_index = self.table_compounds.rowCount()
        # Add all missing vehicle name from active session
        veh_total = api.read.vehicle.total_vehicles()
        for index in range(veh_total):
            class_name = api.read.vehicle.class_name(index)
            compound_names = set(
                (
                    f"{class_name} - {api.read.tyre.compound_name_front(index)}",
                    f"{class_name} - {api.read.tyre.compound_name_rear(index)}",
                )
            )
            for compound in compound_names:
                if not self.is_value_in_table(compound, self.table_compounds):
                    self.add_compound_entry(
                        row_index,
                        compound,
                        set_predefined_compound_symbol(compound),
                    )
                    self.table_compounds.setCurrentCell(row_index, 0)
                    row_index += 1
        # Add new name entry
        if start_index == row_index:
            new_compound_name = self.new_name_increment("New Compound Name", self.table_compounds)
            self.add_compound_entry(row_index, new_compound_name, "?")
            self.table_compounds.setCurrentCell(row_index, 0)

    def add_compound_entry(
        self, row_index: int, compound_name: str, symbol_name: str,
        heatmap_name: str = HEATMAP_DEFAULT_TYRE):
        """Add new compound entry to table"""
        self.table_compounds.insertRow(row_index)
        self.table_compounds.setItem(row_index, 0, QTableWidgetItem(compound_name))
        self.table_compounds.setItem(row_index, 1, QTableWidgetItem(symbol_name))
        self.table_compounds.setCellWidget(row_index, 2, self.__add_option_combolist(heatmap_name))

    def sort_compound(self):
        """Sort compounds in ascending order"""
        if self.table_compounds.rowCount() > 1:
            self.table_compounds.sortItems(0)
            self.set_modified()

    def delete_compound(self):
        """Delete compound entry"""
        selected_rows = set(data.row() for data in self.table_compounds.selectedIndexes())
        if not selected_rows:
            QMessageBox.warning(self, "Error", "No data selected.")
            return

        if not self.confirm_operation(message="<b>Delete selected rows?</b>"):
            return

        for row_index in sorted(selected_rows, reverse=True):
            self.table_compounds.removeRow(row_index)
        self.set_modified()

    def reset_setting(self):
        """Reset setting"""
        msg_text = (
            "Reset <b>compounds preset</b> to default?<br><br>"
            "Changes are only saved after clicking Apply or Save Button."
        )
        if self.confirm_operation(message=msg_text):
            self.compounds_temp = copy_setting(cfg.default.compounds)
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
        item = self.table_compounds.item(row_index, column_index)
        if column_index == 1:  # symbol column
            text = item.text()
            if not text:
                item.setText("?")
            else:
                item.setText(text[:1])

    def update_compounds_temp(self):
        """Update temporary changes to compounds temp first"""
        self.compounds_temp.clear()
        for index in range(self.table_compounds.rowCount()):
            compound_name = self.table_compounds.item(index, 0).text()
            symbol_name = self.table_compounds.item(index, 1).text()
            heatmap_name = self.table_compounds.cellWidget(index, 2).currentText()
            self.compounds_temp[compound_name] = {
                "symbol": symbol_name,
                "heatmap": heatmap_name,
            }

    def save_setting(self):
        """Save setting"""
        self.update_compounds_temp()
        cfg.user.compounds = copy_setting(self.compounds_temp)
        cfg.save(0, cfg_type=ConfigType.COMPOUNDS)
        while cfg.is_saving:  # wait saving finish
            time.sleep(0.01)
        self.reloading()
        self.set_unmodified()
