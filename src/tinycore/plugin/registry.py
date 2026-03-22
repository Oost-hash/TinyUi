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
"""PluginRegistry — manages plugin lifecycle."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tinycore.app import App

    from .protocol import Plugin


class PluginRegistry:
    """Stores plugins and orchestrates two-phase init."""

    def __init__(self):
        self._plugins: list[Plugin] = []

    def add(self, plugin: Plugin) -> None:
        """Add a plugin to the registry."""
        self._plugins.append(plugin)

    def register_all(self, app: App) -> None:
        """Phase 1: call register() on all plugins with a scoped PluginContext."""
        from .context import PluginContext
        for plugin in self._plugins:
            plugin.register(PluginContext(app, plugin.name))

    def start_all(self) -> None:
        """Phase 2: call start() on all plugins in order."""
        for plugin in self._plugins:
            plugin.start()

    def stop_all(self) -> None:
        """Teardown: call stop() on all plugins in reverse order."""
        for plugin in reversed(self._plugins):
            plugin.stop()

    def get(self, name: str) -> Plugin:
        """Return the plugin with the given name."""
        for p in self._plugins:
            if p.name == name:
                return p
        raise KeyError(f"Plugin '{name}' not registered")

    @property
    def plugins(self) -> list[Plugin]:
        return list(self._plugins)
