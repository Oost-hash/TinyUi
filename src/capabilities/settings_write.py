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

"""Settings write capability."""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import QObject, Slot

from runtime.runtime import Runtime


class SettingsWrite(QObject):
    """QML-facing write surface for settings."""

    def __init__(self, runtime: Runtime, settings_read: Any | None = None, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._runtime = runtime
        self._settings_read = settings_read

    @Slot(str, str, str, result=bool)
    def setString(self, namespace: str, key: str, value: str) -> bool:
        registry = self._runtime.settings
        if registry is None:
            return False
        registry.set(namespace, key, value)
        registry.save(namespace)
        if self._settings_read is not None and hasattr(self._settings_read, "refresh"):
            self._settings_read.refresh()
        return True
