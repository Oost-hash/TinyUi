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

"""Widget visibility write capability."""

from __future__ import annotations

from PySide6.QtCore import QObject, Slot

from runtime.runtime import Runtime
from runtime_schema import EventBus, EventType, WidgetRuntimeUpdatedData


class WidgetVisibilityWrite(QObject):
    """Write widget visibility state for QML consumers."""

    def __init__(
        self,
        runtime: Runtime,
        event_bus: EventBus,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._runtime = runtime
        self._event_bus = event_bus

    @Slot(bool)
    def setGlobalVisible(self, visible: bool) -> None:
        """Set global widget visibility state.

        Args:
            visible: True to show all widgets, False to hide all widgets.
        """
        self._runtime.set_global_widgets_visible(visible)

    @Slot(str, str, bool)
    def setWidgetEnabled(self, overlay_id: str, widget_id: str, enabled: bool) -> None:
        """Enable or disable a specific widget.

        Args:
            overlay_id: ID of the overlay plugin.
            widget_id: ID of the widget instance.
            enabled: True to enable, False to disable.
        """
        self._runtime.widget_store.set_widget_enabled(overlay_id, widget_id, enabled)
        self._event_bus.emit_typed(
            EventType.WIDGET_RUNTIME_UPDATED,
            WidgetRuntimeUpdatedData(reason="widget_enabled_changed")
        )
