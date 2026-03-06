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
Track info editor
"""

import logging

from PySide2.QtCore import QPoint, Qt
from PySide2.QtWidgets import (
    QMenu,
    QMessageBox,
    QTableWidgetItem,
    QVBoxLayout,
)

from tinyui.backend.controls import api
from tinyui.backend.constants import ConfigType
from tinyui.backend.settings import cfg, copy_setting
from tinypedal.template.setting_tracks import TRACKINFO_DEFAULT
from .._common import (
    ClockTableItem,
    FloatTableItem,
    TableEditor,
    UIScaler,
    editor_button_bar,
    setup_table,
)

HEADER_TRACKS = (
    "Track name",
    "Pit entry (m)",
    "Pit exit (m)",
    "Pit speed (m/s)",
    "Speed trap (m)",
    "Sunrise",
    "Sunset",
)

logger = logging.getLogger(__name__)


class TrackInfoEditor(TableEditor):
    """Track info editor"""

    def __init__(self, parent):
        super().__init__(parent)
        self.set_utility_title("Track Info Editor")
        self.setMinimumSize(UIScaler.size(64), UIScaler.size(35))

        self.tracks_temp = copy_setting(cfg.user.tracks)

        # Set table
        self.table = setup_table(
            self, HEADER_TRACKS,
            column_widths={
                i: 8 if i <= 4 else 5
                for i in range(1, len(HEADER_TRACKS))
            },
        )
        self.table.cellChanged.connect(self.verify_input)

        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.open_context_menu)

        self.refresh_table()
        self.set_unmodified()

        # Set button
        layout_button = editor_button_bar(self, [
            ("Add", self.add_track),
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
        """Refresh tracks list"""
        self.table.setRowCount(0)
        row_index = 0
        for track_name, track_data in self.tracks_temp.items():
            self.add_track_entry(row_index, track_name, track_data)
            row_index += 1

    def add_track(self):
        """Add new track"""
        start_index = row_index = self.table.rowCount()
        # Add missing track name from active session
        track_name = api.read.session.track_name()
        if track_name and not self.is_value_in_table(track_name, self.table):
            self.add_track_entry(row_index, track_name, TRACKINFO_DEFAULT)
            row_index += 1
        # Add new name entry
        if start_index == row_index:
            new_track_name = self.new_name_increment("New Track Name", self.table)
            self.add_track_entry(row_index, new_track_name, TRACKINFO_DEFAULT)
            self.table.setCurrentCell(row_index, 0)

    def add_track_entry(self, row_index: int, track_name: str, track_data: dict):
        """Add new track entry to table"""
        self.table.insertRow(row_index)
        self.table.setItem(row_index, 0, QTableWidgetItem(track_name))
        column_index = 1
        for key, value in TRACKINFO_DEFAULT.items():
            if isinstance(value, float):
                item = FloatTableItem(track_data.get(key, value))
            else:
                item = ClockTableItem(track_data.get(key, value))
            self.table.setItem(row_index, column_index, item)
            column_index += 1

    def reset_setting(self):
        """Reset setting"""
        msg_text = (
            "Reset <b>tracks preset</b> to default?<br><br>"
            "Changes are only saved after clicking Apply or Save Button."
        )
        if self.confirm_operation(message=msg_text):
            self.tracks_temp = copy_setting(cfg.default.tracks)
            self.set_modified()
            self.refresh_table()

    def verify_input(self, row_index: int, column_index: int):
        """Verify input value"""
        self.set_modified()
        item = self.table.item(row_index, column_index)
        if column_index >= 1:
            item.validate()

    def open_context_menu(self, position: QPoint):
        """Open context menu"""
        if not self.table.itemAt(position):
            return

        menu = QMenu()
        if self.table.currentColumn() == 4:
            menu.addAction("Set from Telemetry")
        else:
            return

        position += QPoint(  # position correction from header
            self.table.verticalHeader().width(),
            self.table.horizontalHeader().height(),
        )
        selected_action = menu.exec_(self.table.mapToGlobal(position))
        if not selected_action:
            return

        action = selected_action.text()
        if action == "Set from Telemetry":
            self.set_position_from_tele()

    def set_position_from_tele(self):
        """Set position from telemetry to selected cell"""
        if len(self.table.selectedIndexes()) != 1:  # limit to one selected cell
            msg_text = (
                "Select <b>one value</b> from <b>Speed trap</b> column to set position."
            )
            QMessageBox.warning(self, "Error", msg_text)
            return

        if api.read.vehicle.in_pits():
            msg_text = "Cannot set speed trap position while in pit lane."
            QMessageBox.warning(self, "Error", msg_text)
            return

        row_index = self.table.currentRow()
        track_name = self.table.item(row_index, 0).text()
        current_name = api.read.session.track_name()
        if track_name != current_name:
            msg_text = (
                f"Unable to set speed trap position for selected track:<br><b>{track_name}</b><br><br>"
                f"Only support to set speed trap position for current track:<br><b>{current_name}</b>"
            )
            QMessageBox.warning(self, "Error", msg_text)
            return

        position = round(api.read.lap.distance(), 4)
        if not self.confirm_operation(
            message=f"Set speed trap at position <b>{position}</b><br>for <b>{track_name}</b>?"):
            return

        self.table.item(row_index, 4).setValue(position)
        self.table.setCurrentCell(-1, -1)  # deselect to avoid mis-clicking

    def update_temp(self):
        """Update temporary changes to tracks temp"""
        self.tracks_temp.clear()
        for row_index in range(self.table.rowCount()):
            track_name = self.table.item(row_index, 0).text()
            self.tracks_temp[track_name] = {
                key: self.table.item(row_index, column_index).value()
                for column_index, key in enumerate(TRACKINFO_DEFAULT, start=1)
            }

    def persist(self):
        """Persist tracks to config"""
        cfg.user.tracks = copy_setting(self.tracks_temp)
        cfg.save(0, cfg_type=ConfigType.TRACKS)
