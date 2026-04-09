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

"""Widget records read capability for runtime V2."""

from __future__ import annotations

from runtimeV2.widgets.contracts import WidgetRecord
from runtimeV2.widgets.store import WidgetRecordsStore


class WidgetRecordsRead:
    """Read projected widget records."""

    def __init__(self, store: WidgetRecordsStore) -> None:
        self._store = store

    def all_widget_records(self) -> list[WidgetRecord]:
        """Return all widget records."""

        return self._store.all_widget_records()

    def records_for_overlay(self, overlay_id: str) -> list[WidgetRecord]:
        """Return records for one overlay."""

        return self._store.records_for_overlay(overlay_id)

    def widget_record(self, overlay_id: str, widget_id: str) -> WidgetRecord | None:
        """Return one widget runtime record."""

        return self._store.widget_record(overlay_id, widget_id)
