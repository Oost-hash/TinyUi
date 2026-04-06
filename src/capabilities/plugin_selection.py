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

"""Plugin selection capability for active plugin context and selection actions."""

from __future__ import annotations

from PySide6.QtCore import Property, QObject, Signal, Slot

from runtime_schema import Event, EventBus, EventType, UIPluginSelectedData


class PluginSelectionApi(QObject):
    """QML-facing active plugin context derived from runtime events."""

    activePluginChanged = Signal(str)

    def __init__(self, event_bus: EventBus, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._event_bus = event_bus
        self._active_plugin: str = ""
        self._subscribe_to_events()

    def _subscribe_to_events(self) -> None:
        self._event_bus.on(EventType.PLUGIN_ACTIVATED, self._on_plugin_activated)

    def _on_plugin_activated(self, event: Event) -> None:
        data = event.data
        self._active_plugin = data.plugin_id
        self.activePluginChanged.emit(self._active_plugin)

    @Property(str, notify=activePluginChanged)
    def activePlugin(self) -> str:
        return self._active_plugin


class PluginSelectionActions(QObject):
    """QML-facing write surface for active plugin selection."""

    def __init__(self, event_bus: EventBus, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._event_bus = event_bus

    @Slot(str, result=bool)
    def setActivePlugin(self, plugin_id: str) -> bool:
        self._event_bus.emit_typed(
            EventType.UI_PLUGIN_SELECTED,
            UIPluginSelectedData(plugin_id=plugin_id),
        )
        return True
