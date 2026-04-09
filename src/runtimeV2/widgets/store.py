#  TinyUI
#  Copyright (C) 2026 Oost-hash
#
#  This file is part of TinyUI.
#
#  TinyUI is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  TinyUI is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#  TinyUI builds on TinyPedal by s-victor (https://github.com/s-victor/TinyPedal),
#  licensed under GPLv3.

"""Widget runtime record storage for runtime V2."""

from __future__ import annotations

from runtimeV2.widgets.contracts import WidgetRecord


class WidgetRecordsStore:
    """Own the current projected widget runtime records."""

    def __init__(self) -> None:
        self._records: list[WidgetRecord] = []

    def set_records(self, records: list[WidgetRecord]) -> None:
        """Replace the current widget runtime records."""

        self._records = list(records)

    def all_widget_records(self) -> list[WidgetRecord]:
        """Return all current widget records."""

        return list(self._records)

    def records_for_overlay(self, overlay_id: str) -> list[WidgetRecord]:
        """Return records for one overlay."""

        return [record for record in self._records if record.overlay_id == overlay_id]

    def widget_record(self, overlay_id: str, widget_id: str) -> WidgetRecord | None:
        """Return one widget runtime record."""

        for record in self._records:
            if record.overlay_id == overlay_id and record.widget_id == widget_id:
                return record
        return None
