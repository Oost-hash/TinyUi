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

"""Widget visibility write capability for runtime V2."""

from __future__ import annotations

from runtimeV2.events.contracts import EventBus, EventType
from runtimeV2.persistence.capabilities.widget_config_write import WidgetConfigWrite
from runtimeV2.widgets.contracts import WidgetVisibilityChangedData


class WidgetVisibilityWrite:
    """Write widget visibility state owned by the widgets domain."""

    def __init__(self, widget_config_write: WidgetConfigWrite, events: EventBus | None = None) -> None:
        self._widget_config_write = widget_config_write
        self._events = events

    def set_global_visible(self, visible: bool) -> None:
        """Set global widget visibility."""

        self._widget_config_write.set_global_widgets_visible(visible)
        self._emit_changed(
            WidgetVisibilityChangedData(
                scope="global",
                global_visible=visible,
            )
        )

    def set_widget_enabled(self, overlay_id: str, widget_id: str, enabled: bool) -> bool:
        """Set one widget enabled state."""

        updated = self._widget_config_write.set_widget_enabled(overlay_id, widget_id, enabled)
        if updated:
            self._emit_changed(
                WidgetVisibilityChangedData(
                    scope="widget",
                    global_visible=True,
                    overlay_id=overlay_id,
                    widget_id=widget_id,
                    enabled=enabled,
                )
            )
        return updated

    def _emit_changed(self, data: WidgetVisibilityChangedData) -> None:
        if self._events is None:
            return
        self._events.emit_typed(
            EventType.WIDGET_VISIBILITY_CHANGED,
            data,
            source="widgets",
        )
