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
"""PluginContext — scoped application context for a single plugin.

Each plugin receives a PluginContext instead of the full App, creating
a VLAN-like boundary: plugins share infrastructure (events, widgets,
editors, providers) but cannot see each other's settings or loaders.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from tinycore.app import App
    from tinycore.config.loader import LoaderRegistry
    from tinycore.config.store import ConfigStore
    from tinycore.settings import SettingsRegistry, SettingsSpec


class ScopedSettings:
    """Settings registry scoped to one plugin — no cross-plugin access."""

    def __init__(self, registry: SettingsRegistry, plugin_name: str) -> None:
        self._registry = registry
        self._name = plugin_name

    def register(self, spec: SettingsSpec) -> None:
        self._registry.register(self._name, spec)

    def get(self, key: str) -> Any:
        return self._registry.get_value(self._name, key)

    def set(self, key: str, value: Any) -> None:
        self._registry.set_value(self._name, key, value)


class ScopedLoaders:
    """Config loader registry scoped to one plugin."""

    def __init__(self, loaders: LoaderRegistry, plugin_name: str) -> None:
        self._loaders = loaders
        self._name = plugin_name

    def register(self, key: str, filename: str, defaults: dict | None = None) -> None:
        self._loaders.register(key, filename, self._name, defaults)

    def load_all(self, store: ConfigStore) -> None:
        self._loaders.load_all(store)

    def load(self, store: ConfigStore, key: str) -> None:
        self._loaders.load_one(store, key)

    def save(self, store: ConfigStore, key: str) -> None:
        self._loaders.save(store, key)


class PluginContext:
    """Scoped application context for a single plugin.

    Plugins receive this instead of the full App — they can only register
    settings and loaders under their own name. Shared infrastructure
    (events, widgets, editors, providers, config) is passed through.
    """

    def __init__(self, app: App, plugin_name: str) -> None:
        self.name      = plugin_name
        self.settings  = ScopedSettings(app.settings, plugin_name)
        self.loaders   = ScopedLoaders(app.loaders, plugin_name)
        self.config    = app.config
        self.widgets   = app.widgets
        self.editors   = app.editors
        self.events    = app.events
        self.providers = app.providers
