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

"""Startup for runtime V2 plugin lifecycle."""

from __future__ import annotations

from dataclasses import dataclass

from runtime_schema import StartupResult, startup_error, startup_ok
from runtimeV2.connectors.startup import ConnectorsStartupResult
from runtimeV2.events import EventsStartupResult
from runtimeV2.plugins.lifecycle import PluginLifecycleStore
from runtimeV2.plugins.register_lifecycle_capabilities import (
    PluginLifecycleCapabilities,
    register_plugin_lifecycle_capabilities,
)
from runtimeV2.plugins.startup import PluginsStartupResult
from runtimeV2.runtime import RuntimeV2


@dataclass(frozen=True)
class PluginLifecycleStartupResult:
    """Result of plugin lifecycle startup."""

    lifecycle: PluginLifecycleStore
    capabilities: PluginLifecycleCapabilities


def startup_plugin_lifecycle(runtime: RuntimeV2) -> StartupResult:
    """Start plugin lifecycle state after persistence and connectors exist."""

    try:
        plugins = runtime.domain_result("plugins", PluginsStartupResult)
        connectors = runtime.domain_result("connectors", ConnectorsStartupResult)
        events = runtime.domain_result("events", EventsStartupResult)
        lifecycle = PluginLifecycleStore(
            registry=plugins.registry,
            connectors=connectors,
            events=events,
        )
        capabilities = register_plugin_lifecycle_capabilities(lifecycle)
        runtime.register_capability("plugin_active_read", capabilities.active_read)
        runtime.register_capability("plugin_active_write", capabilities.active_write)
        runtime.register_capability("plugin_state_read", capabilities.state_read)
        runtime.register_capability("plugin_state_write", capabilities.state_write)
        runtime.register_domain_result("plugins_lifecycle", PluginLifecycleStartupResult(
            lifecycle=lifecycle,
            capabilities=capabilities,
        ))
        return startup_ok()
    except Exception as exc:
        return startup_error(f"Plugin lifecycle startup failed: {exc}")
