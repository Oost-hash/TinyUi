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

"""Plugin read capability."""

from __future__ import annotations

from PySide6.QtCore import Property, QObject, Signal

from runtime.runtime import Runtime


class PluginRead(QObject):
    """Expose plugin metadata sourced from runtime."""

    pluginsChanged = Signal()

    def __init__(self, runtime: Runtime, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._runtime = runtime
        self._plugins = self._build_plugins()

    def _build_plugins(self) -> list[dict]:
        plugins: list[dict] = []
        for plugin_id in self._runtime.plugin_ids():
            manifest = self._runtime.plugin_manifest(plugin_id)
            if manifest is None:
                continue
            windows = [] if manifest.ui is None else manifest.ui.windows
            plugins.append(
                {
                    "id": plugin_id,
                    "type": manifest.plugin_type,
                    "version": manifest.version,
                    "author": manifest.author,
                    "description": manifest.description,
                    "iconUrl": self._runtime.plugin_icon_url(plugin_id),
                    "requires": list(manifest.requires),
                    "windows": [window.id for window in windows],
                    "windowCount": len(windows),
                    "settingCount": len(manifest.settings),
                }
            )
        return plugins

    def refresh(self) -> None:
        self._plugins = self._build_plugins()
        self.pluginsChanged.emit()

    def items(self) -> list[dict]:
        return list(self._plugins)

    @Property(list, notify=pluginsChanged)
    def plugins(self) -> list[dict]:
        return list(self._plugins)
