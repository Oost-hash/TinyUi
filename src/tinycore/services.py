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

"""Core-owned host and runtime service groupings."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from tinyui_schema import EditorRegistry, SettingsSpec

from .capabilities.registry import CapabilityRegistry
from .paths import AppPaths
from .persistence.config.loader import LoaderRegistry
from .persistence.config.store import ConfigStore
from .persistence.settings import SettingsRegistry
from .persistence.widget_state import WidgetStateRegistry
from .runtime.plugins.facts import PluginParticipationFacts
from .runtime.plugins.registry import PluginRuntimeRegistry
from .session.runtime import SessionRuntime


class PersistenceServices:
    """Host-owned persistence services."""

    def __init__(self, paths: AppPaths) -> None:
        self.paths = paths
        self._config = ConfigStore()
        self._loaders = LoaderRegistry(paths.config_dir)
        self._plugin_settings = SettingsRegistry(paths.config_dir)
        self._host_settings = SettingsRegistry(paths.config_dir)
        self._widget_state = WidgetStateRegistry(paths.config_dir)

    def load_all(self) -> None:
        """Load persisted config documents and settings into memory."""
        self._loaders.load_all(self._config)
        self._plugin_settings.load_persisted()
        self._host_settings.load_persisted()

    def register_config(
        self,
        plugin_name: str,
        key: str,
        filename: str,
        defaults: dict[str, Any] | None = None,
    ) -> None:
        """Register one plugin-owned config document."""
        self._loaders.register(key, filename, plugin_name, defaults)

    def load_config(self, key: str) -> None:
        """Load one config document into the shared config store."""
        self._loaders.load_one(self._config, key)

    def load_all_configs(self) -> None:
        """Load all registered config documents into the shared config store."""
        self._loaders.load_all(self._config)

    def save_config(self, key: str) -> None:
        """Save one config document from the shared config store."""
        self._loaders.save(self._config, key)

    def get_config(self, key: str, default: Any = None) -> Any:
        """Read a config document snapshot from the shared config store."""
        return self._config.get_or_default(key, default)

    def update_config(self, key: str, value: Any) -> None:
        """Publish a new config document snapshot to the shared config store."""
        self._config.update(key, value)

    def observe_config(self, key: str, callback: Callable[[Any], None]) -> Callable[[], None]:
        """Subscribe to changes for a config document key."""
        return self._config.observe(key, callback)

    def register_plugin_setting(self, plugin_name: str, spec: SettingsSpec) -> None:
        """Register a plugin-owned setting."""
        self._plugin_settings.register(plugin_name, spec)

    def register_host_setting(self, plugin_name: str, spec: SettingsSpec) -> None:
        """Register a host-owned setting."""
        self._host_settings.register(plugin_name, spec)

    def settings_groups(self) -> list[tuple[str, list[SettingsSpec]]]:
        """Return host settings first, then plugin settings."""
        groups: list[tuple[str, list[SettingsSpec]]] = []
        for registry in (self._host_settings, self._plugin_settings):
            groups.extend(registry.by_plugin().items())
        return groups

    def has_host_settings(self, plugin_name: str) -> bool:
        """Return True when the plugin name belongs to host-owned settings."""
        return self._host_settings.has_plugin(plugin_name)

    def get_setting(self, plugin_name: str, key: str) -> Any:
        """Read a persisted setting from the right registry."""
        registry = (
            self._host_settings if self.has_host_settings(plugin_name) else self._plugin_settings
        )
        return registry.get_value(plugin_name, key)

    def set_setting(self, plugin_name: str, key: str, value: Any) -> None:
        """Write a persisted setting into the right registry."""
        registry = (
            self._host_settings if self.has_host_settings(plugin_name) else self._plugin_settings
        )
        registry.set_value(plugin_name, key, value)

    def load_all_settings(self) -> None:
        """Load both host and plugin settings from disk."""
        self._plugin_settings.load_persisted()
        self._host_settings.load_persisted()

    def save_settings(self, plugin_name: str) -> None:
        """Persist one plugin or host settings group to disk."""
        registry = (
            self._host_settings if self.has_host_settings(plugin_name) else self._plugin_settings
        )
        registry.save(plugin_name)

    def widget_state_for(self, plugin_name: str):
        """Return the widget state store for one plugin."""
        return self._widget_state.for_plugin(plugin_name)


@dataclass(frozen=True)
class HostServices:
    """Host-owned persistence and declaration services."""

    persistence: PersistenceServices
    editors: EditorRegistry


@dataclass(frozen=True)
class RuntimeServices:
    """Runtime-owned participation services with session as backing compatibility state."""

    session: SessionRuntime
    plugin_facts: PluginParticipationFacts
    plugin_runtime: PluginRuntimeRegistry


def build_host_services(paths: AppPaths) -> HostServices:
    """Create the host-owned service group for one runtime composition."""
    return HostServices(
        persistence=PersistenceServices(paths),
        editors=EditorRegistry(),
    )


def build_runtime_services() -> RuntimeServices:
    """Create the runtime-owned service group for one runtime composition."""
    capabilities = CapabilityRegistry()
    session = SessionRuntime(capabilities)
    return RuntimeServices(
        session=session,
        plugin_facts=PluginParticipationFacts(session),
        plugin_runtime=PluginRuntimeRegistry(),
    )
