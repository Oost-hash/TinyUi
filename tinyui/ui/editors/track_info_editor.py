"""Track info editor - refactored to use GenericDictTableEditor."""

from PySide2.QtCore import QPoint
from PySide2.QtWidgets import (
    QMenu,
    QMessageBox,
    QTableWidgetItem,
)

from tinyui.backend.constants import ConfigType
from tinyui.backend.controls import api
from tinyui.backend.data import TRACKINFO_DEFAULT

from ..components.table_items import ClockTableItem, FloatTableItem
from ._generic_dict_editor import GenericDictTableEditor


class TrackInfoEditor(GenericDictTableEditor):
    """Track info editor."""

    _cfg_attr = "tracks"
    _cfg_type = ConfigType.TRACKS
    _title = "Track Info Editor"
    _columns = (
        "Track name",
        "Pit entry (m)",
        "Pit exit (m)",
        "Pit speed (m/s)",
        "Speed trap (m)",
        "Sunrise",
        "Sunset",
    )
    _column_widths = {i: 8 if i <= 4 else 5 for i in range(1, 7)}
    _min_size = (64, 35)

    def __init__(self, parent):
        super().__init__(parent)
        # Add context menu
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._open_context_menu)

    def _row_to_widgets(self, key: str, data: dict) -> list:
        """Convert track data to table row."""
        items = [QTableWidgetItem(key)]
        for field_key, default in TRACKINFO_DEFAULT.items():
            value = data.get(field_key, default)
            if isinstance(default, float):
                items.append(FloatTableItem(value))
            else:
                items.append(ClockTableItem(value))
        return items

    def _row_to_dict(self, row_idx: int) -> dict:
        """Extract track data from table row."""
        return {
            key: self.table.item(row_idx, col_idx).value()
            for col_idx, key in enumerate(TRACKINFO_DEFAULT.keys(), start=1)
        }

    def add_row(self):
        """Add new track - auto-import from API or create new."""
        track_name = api.read.session.track_name()

        if track_name and not self.is_value_in_table(track_name, self.table):
            widgets = self._row_to_widgets(track_name, TRACKINFO_DEFAULT)
            row_idx = self.table.rowCount()
            self.table.insert_row(row_idx, widgets)
            self.table.setCurrentCell(row_idx, 0)
            self.set_modified()
        else:
            super().add_row()

    def _open_context_menu(self, position: QPoint):
        """Open context menu for speed trap column."""
        if not self.table.itemAt(position):
            return

        if self.table.currentColumn() != 4:  # Speed trap column
            return

        menu = QMenu()
        menu.addAction("Set from Telemetry").triggered.connect(self._set_from_telemetry)

        # Position correction
        position += QPoint(
            self.table.verticalHeader().width(),
            self.table.horizontalHeader().height(),
        )
        menu.exec_(self.table.mapToGlobal(position))

    def _set_from_telemetry(self):
        """Set speed trap position from telemetry."""
        if len(self.table.selectedIndexes()) != 1:
            QMessageBox.warning(
                self, "Error", "Select one value from Speed trap column."
            )
            return

        if api.read.vehicle.in_pits():
            QMessageBox.warning(self, "Error", "Cannot set position while in pit lane.")
            return

        row_idx = self.table.currentRow()
        track_name = self.table.item(row_idx, 0).text()
        current_track = api.read.session.track_name()

        if track_name != current_track:
            QMessageBox.warning(
                self,
                "Error",
                f"Cannot set for <b>{track_name}</b>.<br><br>"
                f"Only current track: <b>{current_track}</b>",
            )
            return

        position = round(api.read.lap.distance(), 4)
        if not self.confirm_operation(
            message=f"Set speed trap at <b>{position}</b> for <b>{track_name}</b>?"
        ):
            return

        self.table.item(row_idx, 4).setValue(position)
        self.table.setCurrentCell(-1, -1)
