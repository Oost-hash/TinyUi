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

"""Menu capability for QML-facing host and plugin menu contributions."""

from __future__ import annotations

from PySide6.QtCore import Property, QObject, Signal

from runtime_schema import Event, EventBus, EventType


class MenuApi(QObject):
    """QML-facing menu contribution model derived from runtime events."""

    menuItemsChanged = Signal()
    pluginMenuItemsChanged = Signal()

    def __init__(self, event_bus: EventBus, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._event_bus = event_bus
        self._menu_items: list[dict] = []
        self._plugin_menu_labels: dict[str, str] = {}
        self._plugin_menu_items: dict[str, list[dict]] = {}
        self._active_plugin: str = ""
        self._subscribe_to_events()

    def _subscribe_to_events(self) -> None:
        self._event_bus.on(EventType.MENU_REGISTERED, self._on_menu_registered, replay_history=True)
        self._event_bus.on(EventType.PLUGIN_ACTIVATED, self._on_plugin_activated)

    def _on_plugin_activated(self, event: Event) -> None:
        data = event.data
        self._active_plugin = data.plugin_id
        self.pluginMenuItemsChanged.emit()

    def _on_menu_registered(self, event: Event) -> None:
        data = event.data
        if data.separator:
            item = {"separator": True, "label": ""}
        else:
            item = {"label": data.label, "action": data.action}

        if data.source == "host":
            self._menu_items.append(item)
            self.menuItemsChanged.emit()
            return

        window_id = data.window_id
        if window_id.startswith("plugin:"):
            plugin_id = window_id.replace("plugin:", "")
            label = plugin_id.replace("_", " ").title()
            if plugin_id not in self._plugin_menu_items:
                self._plugin_menu_labels[plugin_id] = label
                self._plugin_menu_items[plugin_id] = []
            self._plugin_menu_items[plugin_id].append(item)
            self.pluginMenuItemsChanged.emit()

    @Property(list, notify=menuItemsChanged)
    def menuItems(self) -> list[dict]:
        return self._menu_items

    @Property(list, notify=pluginMenuItemsChanged)
    def pluginMenuItems(self) -> list[dict]:
        if self._active_plugin and self._active_plugin in self._plugin_menu_items:
            return self._plugin_menu_items[self._active_plugin]
        return []

    @Property(str, notify=pluginMenuItemsChanged)
    def pluginMenuLabel(self) -> str:
        if self._active_plugin and self._active_plugin in self._plugin_menu_labels:
            return self._plugin_menu_labels[self._active_plugin]
        return ""
