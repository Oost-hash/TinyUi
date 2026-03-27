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

Each plugin receives a PluginContext instead of the full host composition, creating
a VLAN-like boundary: plugins share scoped host services without seeing
the host's internal registries or stores.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from tinycore.capabilities.registry import CapabilityBinding
    from tinycore.runtime.plugins.facts import PluginParticipationFacts
    from tinycore.services import PersistenceServices
    from tinyui_schema import EditorRegistry
    from tinyui_schema import SettingsSpec


class ScopedCapabilities:
    """Capability bindings scoped to one consumer plugin."""

    def __init__(
        self,
        participation: PluginParticipationFacts,
        plugin_name: str,
        required: tuple[str, ...],
    ) -> None:
        self._participation = participation
        self._plugin_name = plugin_name
        self._required = required

    def required(self) -> tuple[str, ...]:
        """Declared capability requirements for this plugin."""
        return self._required

    def all(self) -> dict[str, CapabilityBinding]:
        """All resolved bindings currently known for this plugin."""
        return dict(self._participation.bindings_for(self._plugin_name).resolved)

    def get(self, capability: str) -> CapabilityBinding | None:
        """Resolve a capability if it was declared by this plugin."""
        if capability not in self._required:
            raise KeyError(f"Capability '{capability}' was not declared in requires")
        return self._participation.bindings_for(self._plugin_name).get(capability)

    def require(self, capability: str) -> CapabilityBinding:
        """Resolve a declared capability or raise KeyError."""
        if capability not in self._required:
            raise KeyError(f"Capability '{capability}' was not declared in requires")
        return self._participation.bindings_for(self._plugin_name).require(capability)


class ScopedSettings:
    """Settings registry scoped to one plugin — no cross-plugin access."""

    def __init__(self, persistence: PersistenceServices, plugin_name: str) -> None:
        self._persistence = persistence
        self._name = plugin_name

    def register(self, spec: SettingsSpec) -> None:
        self._persistence.register_plugin_setting(self._name, spec)

    def get(self, key: str) -> Any:
        return self._persistence.get_setting(self._name, key)

    def set(self, key: str, value: Any) -> None:
        self._persistence.set_setting(self._name, key, value)


class ScopedConfig:
    """Plugin-scoped config document access."""

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


class ScopedEditors:
    """Editor registration scoped to one plugin."""

    def __init__(self, registry: EditorRegistry) -> None:
        self._registry = registry

    def register(self, spec) -> None:
        self._registry.register(spec)


class PluginContext:
    """Scoped application context for a single plugin.

    Plugins receive this instead of the full host composition. Scoped services such as
    settings, config loading, and capabilities are exposed directly, while
    the host keeps ownership of its runtime internals.
    """

    def __init__(
        self,
        persistence: PersistenceServices,
        editors: EditorRegistry,
        participation: PluginParticipationFacts,
        plugin_name: str,
        requires: tuple[str, ...] = (),
    ) -> None:
        self.name = plugin_name
        self.settings = ScopedSettings(persistence, plugin_name)
        self.config = ScopedConfig(persistence, plugin_name)
        self.loaders = self.config
        self.capabilities = ScopedCapabilities(participation, plugin_name, requires)
        self.editors = ScopedEditors(editors)
