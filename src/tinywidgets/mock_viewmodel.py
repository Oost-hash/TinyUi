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
"""MockViewModel — QML bridge for the mock/demo connector.

Lets the user toggle demo mode and edit its min, max and speed from
the widget settings panel without touching the composition root at runtime.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Property, QObject, Signal, Slot

if TYPE_CHECKING:
    from plugins.demo.connector.mock import MockConnector
    from tinycore.telemetry.registry import ConnectorRegistry


class MockViewModel(QObject):
    """Controls the mock connector for a single plugin slot.

    When active the mock connector is swapped into the ConnectorRegistry so
    every widget running on that plugin sees simulated data instead of live
    telemetry.
    """

    activeChanged = Signal()
    configChanged = Signal()

    def __init__(
        self,
        registry:       "ConnectorRegistry",
        plugin_name:    str,
        real_connector,
        mock_connector: "MockConnector",
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._registry    = registry
        self._plugin_name = plugin_name
        self._real        = real_connector
        self._mock        = mock_connector
        self._active      = False

    # ── Slots ─────────────────────────────────────────────────────────────────

    @Slot()
    def toggle(self) -> None:
        self._active = not self._active
        self._registry.register(
            self._plugin_name,
            self._mock if self._active else self._real,
        )
        self.activeChanged.emit()

    @Slot(float)
    def setMin(self, value: float) -> None:
        self._mock.configure(value, self._mock.max_val, self._mock.step)
        self.configChanged.emit()

    @Slot(float)
    def setMax(self, value: float) -> None:
        self._mock.configure(self._mock.min_val, value, self._mock.step)
        self.configChanged.emit()

    @Slot(float)
    def setSpeed(self, value: float) -> None:
        self._mock.configure(self._mock.min_val, self._mock.max_val, value)
        self.configChanged.emit()

    # ── Properties ────────────────────────────────────────────────────────────

    @Property(bool, notify=activeChanged)
    def active(self) -> bool:
        return self._active

    @Property(float, notify=configChanged)
    def demoMin(self) -> float:
        return self._mock.min_val

    @Property(float, notify=configChanged)
    def demoMax(self) -> float:
        return self._mock.max_val

    @Property(float, notify=configChanged)
    def demoSpeed(self) -> float:
        return self._mock.step
