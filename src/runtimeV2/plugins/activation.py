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

"""Plugin activation adapters for runtime V2."""

from __future__ import annotations

import importlib
import importlib.util
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from runtimeV2.connectors.service_registry import ConnectorServiceRegistry
from runtimeV2.persistence.stores.settings import SettingsStore
from runtimeV2.plugins.contracts import PluginContext
from runtimeV2.plugins.registry import PluginRegistry


class PluginActivation(Protocol):
    """Common runtime V2 plugin activation surface."""

    def activate(self, ctx: PluginContext) -> None:
        """Activate plugin resources for the given context."""

    def deactivate(self, ctx: PluginContext) -> None:
        """Release plugin resources for the given context."""


@dataclass(frozen=True)
class NoOpPluginActivation:
    """Activation adapter for manifest-only plugins."""

    plugin_id: str

    def activate(self, ctx: PluginContext) -> None:
        """Manifest-driven plugins need no Python activation step."""

    def deactivate(self, ctx: PluginContext) -> None:
        """Manifest-driven plugins need no Python deactivation step."""


@dataclass(frozen=True)
class PythonModulePluginActivation:
    """Activation adapter backed by a plugin.py module."""

    plugin_id: str

    @property
    def module_name(self) -> str:
        return f"plugins.{self.plugin_id}.plugin"

    def activate(self, ctx: PluginContext) -> None:
        """Import plugin module and call activate if provided."""

        module = importlib.import_module(self.module_name)
        if hasattr(module, "activate"):
            module.activate(ctx)

    def deactivate(self, ctx: PluginContext) -> None:
        """Import plugin module and call deactivate if provided."""

        module = importlib.import_module(self.module_name)
        if hasattr(module, "deactivate"):
            module.deactivate(ctx)


class ScopedPluginSettings:
    """Plugin-scoped settings facade built on top of V2 persistence."""

    def __init__(self, store: SettingsStore, namespace: str) -> None:
        self._store = store
        self._namespace = namespace

    def get(self, key: str):
        """Return one plugin-scoped setting value."""

        return self._store.get(self._namespace, key)

    def values(self) -> dict[str, object]:
        """Return all values for this plugin namespace."""

        return self._store.namespace_values(self._namespace)

    def set(self, key: str, value: object) -> None:
        """Set one plugin-scoped setting value."""

        self._store.set(self._namespace, key, value)

    def save(self) -> None:
        """Save the current plugin namespace."""

        self._store.save(self._namespace)


class PluginActivationStore:
    """Resolve and execute plugin activation for runtime V2."""

    def __init__(
        self,
        *,
        registry: PluginRegistry,
        settings: SettingsStore,
        connector_services: ConnectorServiceRegistry,
    ) -> None:
        self._registry = registry
        self._settings = settings
        self._connector_services = connector_services
        self._resolved: dict[str, PluginActivation] = {}

    def activate_plugin(self, plugin_id: str) -> None:
        """Activate one discovered plugin."""

        activation = self._resolve_activation(plugin_id)
        activation.activate(self._context(plugin_id))

    def deactivate_plugin(self, plugin_id: str) -> None:
        """Deactivate one discovered plugin."""

        activation = self._resolve_activation(plugin_id)
        activation.deactivate(self._context(plugin_id))

    def _context(self, plugin_id: str) -> PluginContext:
        return PluginContext(
            plugin_id=plugin_id,
            settings=ScopedPluginSettings(self._settings, plugin_id),
            connector_services=self._connector_services,
        )

    def _resolve_activation(self, plugin_id: str) -> PluginActivation:
        activation = self._resolved.get(plugin_id)
        if activation is not None:
            return activation

        plugin_root = self._registry.plugin_root(plugin_id)
        if plugin_root is None:
            raise KeyError(f"Plugin root is not available: {plugin_id}")

        activation = resolve_plugin_activation(plugin_id=plugin_id, plugin_root=plugin_root)
        self._resolved[plugin_id] = activation
        return activation


def resolve_plugin_activation(*, plugin_id: str, plugin_root: Path) -> PluginActivation:
    """Resolve the activation adapter for one plugin root."""

    module_path = plugin_root / "plugin.py"
    module_pyc = plugin_root / "plugin.pyc"
    module_name = f"plugins.{plugin_id}.plugin"
    try:
        spec_exists = importlib.util.find_spec(module_name) is not None
    except ModuleNotFoundError:
        spec_exists = False

    if module_path.exists() or module_pyc.exists() or spec_exists:
        return PythonModulePluginActivation(plugin_id)
    return NoOpPluginActivation(plugin_id)
