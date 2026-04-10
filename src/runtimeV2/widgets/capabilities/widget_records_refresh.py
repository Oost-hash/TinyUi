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

"""Widget runtime record refresh capability."""

from __future__ import annotations

from runtimeV2.events.contracts import EventBus, EventType
from runtimeV2.widgets.contracts import WidgetRecord, WidgetRuntimeUpdatedData
from runtimeV2.widgets.projection import project_widget_records
from runtimeV2.widgets.store import WidgetRecordsStore


class WidgetRecordsRefresh:
    """Refresh projected widget records when runtime dependencies change."""

    def __init__(
        self,
        *,
        store: WidgetRecordsStore,
        overlay_read,
        connector_decl_read,
        connector_read,
        active_read,
        widget_config_read,
        events: EventBus,
    ) -> None:
        self._store = store
        self._overlay_read = overlay_read
        self._connector_decl_read = connector_decl_read
        self._connector_read = connector_read
        self._active_read = active_read
        self._widget_config_read = widget_config_read
        self._events = events

    def refresh(self) -> list[WidgetRecord]:
        """Refresh and return current widget runtime records."""

        records = project_widget_records(
            overlay_read=self._overlay_read,
            connector_decl_read=self._connector_decl_read,
            connector_read=self._connector_read,
            active_read=self._active_read,
            widget_config_read=self._widget_config_read,
        )
        self._store.set_records(records)
        self._events.emit_typed(
            EventType.WIDGET_RUNTIME_UPDATED,
            WidgetRuntimeUpdatedData(widget_count=len(records)),
            source="widgets",
        )
        return records
