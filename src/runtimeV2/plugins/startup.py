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

from runtime_schema import Event, EventType, StartupResult, startup_error, startup_ok
from runtimeV2.events import EventsStartupResult
from runtimeV2.paths import PathsStartupResult
from runtimeV2.plugins.discovery import discover_plugins
from runtimeV2.plugins.register_capabilities import PluginCapabilities, register_plugin_capabilities
from runtimeV2.plugins.register_events import register_plugin_events
from runtimeV2.plugins.registry import PluginRegistry
from runtimeV2.runtime import RuntimeV2


@dataclass(frozen=True)
class PluginsStartupResult:
    """Result of plugins discovery startup."""

    registry: PluginRegistry
    capabilities: PluginCapabilities


def startup_plugins(runtime: RuntimeV2) -> StartupResult:
    """Start read-only plugin discovery."""

    try:
        paths_result = runtime.domain_result("paths", PathsStartupResult)
        events_result = runtime.domain_result("events", EventsStartupResult)
        register_plugin_events(events_result.registry)

        registry = discover_plugins(paths_result.runtime_paths)
        capabilities = register_plugin_capabilities(registry)
        runtime.register_capability("plugin_discovery", capabilities.discovery)
        runtime.register_capability("plugin_manifest_read", capabilities.manifest_read)
        runtime.register_capability("plugin_settings_spec_read", capabilities.settings_spec_read)
        runtime.register_capability("plugin_ui_manifest_read", capabilities.ui_manifest_read)
        runtime.register_capability("plugin_connector_decl_read", capabilities.connector_decl_read)
        runtime.register_capability("plugin_overlay_decl_read", capabilities.overlay_decl_read)
        runtime.register_capability("plugin_icon", capabilities.icon)
        runtime.register_domain_result("plugins", PluginsStartupResult(
            registry=registry,
            capabilities=capabilities,
        ))
        events_result.bus.emit(Event(EventType.PLUGINS_DISCOVERED, data=None, source="plugins"))
        return startup_ok()
    except Exception as exc:
        return startup_error(f"Plugins domain startup failed: {exc}")
