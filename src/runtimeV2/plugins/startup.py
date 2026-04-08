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

"""Startup for runtime V2 plugins discovery."""

from __future__ import annotations

from dataclasses import dataclass

from runtimeV2.connectors.startup import ConnectorsStartupResult
from runtimeV2.events.contracts import Event, EventType
from runtimeV2.events.startup import EventsStartupResult
from runtimeV2.manifest.capabilities.load import ManifestLoad
from runtimeV2.manifest.capabilities.manifest_read import ManifestRead
from runtimeV2.paths.startup import PathsStartupResult
from runtimeV2.plugins.discovery import discover_plugins
from runtimeV2.plugins.lifecycle import PluginLifecycleStore
from runtimeV2.plugins.register_capabilities import PluginCapabilities, register_plugin_capabilities
from runtimeV2.plugins.register_events import register_plugin_events
from runtimeV2.plugins.register_lifecycle_capabilities import (
    PluginLifecycleCapabilities,
    register_plugin_lifecycle_capabilities,
)
from runtimeV2.plugins.registry import PluginRegistry
from runtimeV2.runtime import RuntimeV2
from runtimeV2.schemas.startup import StartupResult, startup_error, startup_ok


@dataclass(frozen=True)
class PluginsStartupResult:
    """Result of plugins discovery startup."""

    registry: PluginRegistry
    capabilities: PluginCapabilities
    lifecycle: PluginLifecycleStore | None = None
    lifecycle_capabilities: PluginLifecycleCapabilities | None = None


def startup_plugins(runtime: RuntimeV2) -> StartupResult:
    """Start read-only plugin discovery."""

    try:
        paths_result = runtime.domain_result("paths", PathsStartupResult)
        events_result = runtime.domain_result("events", EventsStartupResult)
        register_plugin_events(events_result.registry)

        manifest_load = runtime.capability("manifest_load", ManifestLoad)
        manifest_read = runtime.capability("manifest_read", ManifestRead)
        registry = discover_plugins(paths_result.runtime_paths, manifest_load)
        capabilities = register_plugin_capabilities(registry, manifest_read)
        runtime.register_capability("plugin_discovery", capabilities.discovery)
        runtime.register_capability("plugin_icon", capabilities.icon)
        runtime.register_domain_result("plugins", PluginsStartupResult(
            registry=registry,
            capabilities=capabilities,
        ))
        events_result.bus.emit(Event(EventType.PLUGINS_DISCOVERED, data=None, source="plugins"))
        return startup_ok()
    except Exception as exc:
        return startup_error(f"Plugins domain startup failed: {exc}")


def startup_plugins_lifecycle(runtime: RuntimeV2) -> StartupResult:
    """Start the plugins-owned lifecycle slice after connectors exist."""

    try:
        plugins = runtime.domain_result("plugins", PluginsStartupResult)
        if plugins.lifecycle is not None:
            return startup_ok()

        connectors = runtime.domain_result("connectors", ConnectorsStartupResult)
        events = runtime.domain_result("events", EventsStartupResult)
        lifecycle = PluginLifecycleStore(
            registry=plugins.registry,
            manifest_read=runtime.capability("manifest_read", ManifestRead),
            connectors=connectors,
            events=events,
        )
        lifecycle_capabilities = register_plugin_lifecycle_capabilities(lifecycle)
        runtime.register_capability("plugin_active_read", lifecycle_capabilities.active_read)
        runtime.register_capability("plugin_active_write", lifecycle_capabilities.active_write)
        runtime.register_capability("plugin_state_read", lifecycle_capabilities.state_read)
        runtime.register_capability("plugin_state_write", lifecycle_capabilities.state_write)
        runtime.register_domain_result("plugins", PluginsStartupResult(
            registry=plugins.registry,
            capabilities=plugins.capabilities,
            lifecycle=lifecycle,
            lifecycle_capabilities=lifecycle_capabilities,
        ))
        return startup_ok()
    except Exception as exc:
        return startup_error(f"Plugin lifecycle startup failed: {exc}")
