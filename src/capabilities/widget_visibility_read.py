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

"""Widget visibility read capability."""

from __future__ import annotations

from PySide6.QtCore import QObject, Property, Signal, Slot

from runtime.runtime import Runtime
from runtime_schema import EventBus, EventType


class WidgetVisibilityRead(QObject):
    """Read widget visibility state for QML consumers."""

    globalVisibleChanged = Signal()

    def __init__(
        self,
        runtime: Runtime,
        event_bus: EventBus,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._runtime = runtime
        self._event_bus = event_bus
        self._subscribe()

    def _subscribe(self) -> None:
        """Subscribe to widget runtime events to emit change signals."""
        self._event_bus.on(EventType.WIDGET_RUNTIME_UPDATED, self._on_widget_event)

    def _on_widget_event(self, _event) -> None:
        """Emit change signal when widget visibility may have changed."""
        self.globalVisibleChanged.emit()

    @Property(bool, notify=globalVisibleChanged)
    def globalVisible(self) -> bool:
        """Get global widget visibility state."""
        return self._runtime.is_global_widgets_visible()

    @Slot(str, str, result=bool)
    def isWidgetEnabled(self, overlay_id: str, widget_id: str) -> bool:
        """Check if a specific widget is enabled.

        Args:
            overlay_id: ID of the overlay plugin.
            widget_id: ID of the widget instance.

        Returns:
            True if the widget is enabled, False otherwise.
        """
        config = self._runtime.widget_store.get_widget(overlay_id, widget_id)
        if config is None:
            return True  # Default to enabled if no config exists
        return config.enabled
