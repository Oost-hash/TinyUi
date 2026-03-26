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
"""PluginRegistry — stores consumer plugins and orchestrates their lifecycle."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tinycore.app import App

    from .protocol import Plugin


@dataclass(frozen=True)
class RegisteredPlugin:
    """A plugin instance plus its manifest-owned runtime metadata."""

    plugin: Plugin
    requires: tuple[str, ...] = ()


class PluginRegistry:
    """Stores consumer plugins and orchestrates two-phase init."""

    def __init__(self):
        self._plugins: list[RegisteredPlugin] = []

    def add(self, plugin: Plugin, requires: tuple[str, ...] = ()) -> None:
        """Add a plugin to the registry."""
        self._plugins.append(RegisteredPlugin(plugin=plugin, requires=requires))

    def register_all(self, app: App) -> None:
        """Phase 1: call register() on all plugins with a scoped PluginContext."""
        from .context import PluginContext
        for entry in self._plugins:
            entry.plugin.register(PluginContext(app, entry.plugin.name, entry.requires))

    def start_all(self) -> None:
        """Phase 2: call start() on all plugins in order."""
        for entry in self._plugins:
            entry.plugin.start()

    def stop_all(self) -> None:
        """Teardown: call stop() on all plugins in reverse order."""
        for entry in reversed(self._plugins):
            entry.plugin.stop()

    def get(self, name: str) -> Plugin:
        """Return the plugin with the given name."""
        for entry in self._plugins:
            if entry.plugin.name == name:
                return entry.plugin
        raise KeyError(f"Plugin '{name}' not registered")

    @property
    def plugins(self) -> list[Plugin]:
        return [entry.plugin for entry in self._plugins]
