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

"""Statusbar capability for QML-facing statusbar contributions."""

from __future__ import annotations

from PySide6.QtCore import Property, QObject, Signal

from runtime_schema import Event, EventBus, EventType


class StatusbarApi(QObject):
    """QML-facing statusbar contribution model derived from runtime events."""

    statusbarItemsChanged = Signal()

    def __init__(self, event_bus: EventBus, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._event_bus = event_bus
        self._statusbar_left: list[dict] = []
        self._statusbar_right: list[dict] = []
        self._subscribe_to_events()

    def _subscribe_to_events(self) -> None:
        self._event_bus.on(EventType.STATUSBAR_REGISTERED, self._on_statusbar_registered, replay_history=True)

    def _on_statusbar_registered(self, event: Event) -> None:
        data = event.data
        item = {
            "icon": data.icon,
            "text": data.text,
            "tooltip": data.tooltip,
            "action": data.action,
        }
        if data.side == "left":
            self._statusbar_left.append(item)
        else:
            self._statusbar_right.append(item)
        self.statusbarItemsChanged.emit()

    @Property(list, notify=statusbarItemsChanged)
    def leftItems(self) -> list[dict]:
        return self._statusbar_left

    @Property(list, notify=statusbarItemsChanged)
    def rightItems(self) -> list[dict]:
        return self._statusbar_right
