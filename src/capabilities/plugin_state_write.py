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

"""Plugin state write capability."""

from __future__ import annotations

from PySide6.QtCore import QObject, Slot

from runtime.runtime import Runtime


class PluginStateWrite(QObject):
    """QML-facing write surface for plugin lifecycle controls."""

    def __init__(self, runtime: Runtime, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._runtime = runtime

    @Slot(str, result=bool)
    def enablePlugin(self, plugin_id: str) -> bool:
        return self._runtime.enable_plugin(plugin_id)

    @Slot(str, result=bool)
    def disablePlugin(self, plugin_id: str) -> bool:
        return self._runtime.disable_plugin(plugin_id)
