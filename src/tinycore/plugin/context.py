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
"""Stable plugin-facing context built from the runtime participation seam."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from tinycore.runtime.plugins.exports import ParticipantExports
    from tinycore.runtime.plugins.facts import PluginParticipationFacts
    from tinycore.services import PersistenceServices
    from tinyui_schema import EditorRegistry
    from tinyui_schema import SettingsSpec


class PluginSettings:
    """Settings access scoped to one plugin."""

    def __init__(self, persistence: PersistenceServices, plugin_name: str) -> None:
        self._persistence = persistence
        self._name = plugin_name

    def register(self, spec: SettingsSpec) -> None:
        self._persistence.register_plugin_setting(self._name, spec)

    def get(self, key: str) -> Any:
        return self._persistence.get_setting(self._name, key)

    def set(self, key: str, value: Any) -> None:
        self._persistence.set_setting(self._name, key, value)


class PluginConfig:
    """Config document access scoped to one plugin."""

    def __init__(self, persistence: PersistenceServices, plugin_name: str) -> None:
        self._persistence = persistence
        self._name = plugin_name

    def register(self, key: str, filename: str, defaults: dict | None = None) -> None:
        self._persistence.register_config(self._name, key, filename, defaults)

    def load_all(self) -> None:
        self._persistence.load_all_configs()

    def load(self, key: str) -> None:
        self._persistence.load_config(key)

    def save(self, key: str) -> None:
        self._persistence.save_config(key)

    def get(self, key: str, default: Any = None) -> Any:
        return self._persistence.get_config(key, default)

    def set(self, key: str, value: Any) -> None:
        self._persistence.update_config(key, value)


class PluginEditors:
    """Editor registration scoped to one plugin."""

    def __init__(self, registry: EditorRegistry) -> None:
        self._registry = registry

    def register(self, spec) -> None:
        self._registry.register(spec)


class PluginContext:
    """Stable plugin API surface for scoped host and runtime access."""

    exports: "ParticipantExports"

    def __init__(
        self,
        persistence: PersistenceServices,
        editors: EditorRegistry,
        participation: PluginParticipationFacts,
        plugin_name: str,
        requires: tuple[str, ...] = (),
    ) -> None:
        self.name = plugin_name
        self.settings = PluginSettings(persistence, plugin_name)
        self.config = PluginConfig(persistence, plugin_name)
        self.exports = participation.exports_for(plugin_name, requires)
        self.editors = PluginEditors(editors)
