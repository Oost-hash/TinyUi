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

"""Plugin domain startup — discovers plugins and initializes lifecycle."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from runtime.app.paths import AppPaths
    from runtime.plugins.discovery import PluginDiscovery
    from runtime.plugins.lifecycle_manager import PluginLifecycleManager
    from runtime_schema import EventBus
    from runtime_schema.startup import StartupResult


@dataclass
class PluginsStartupResult:
    """Result of plugins startup."""

    discovery: "PluginDiscovery"
    lifecycle: "PluginLifecycleManager"


# Module-level storage
_plugins_result: PluginsStartupResult | None = None


def startup_plugins(
    event_bus: EventBus,
    paths: AppPaths,
) -> StartupResult:
    """Startup function for plugins domain.

    Discovers all plugins and initializes lifecycle management.

    Args:
        event_bus: Event bus for plugin events.
        paths: Application paths for plugin discovery.

    Returns:
        StartupResult with ok=True on success.
    """
    from runtime_schema.startup import startup_ok, startup_error
    global _plugins_result

    try:
        # 1. Discover all plugins
        from runtime.plugins.discovery import PluginDiscovery
        discovery = PluginDiscovery(paths)
        discovery.discover_all()

        # 2. Initialize lifecycle manager
        from runtime.plugins.lifecycle_manager import PluginLifecycleManager
        lifecycle = PluginLifecycleManager(discovery, event_bus)

        # 3. Store result
        _plugins_result = PluginsStartupResult(
            discovery=discovery,
            lifecycle=lifecycle,
        )

        return startup_ok()

    except Exception as e:
        _plugins_result = None
        return startup_error(f"Plugins startup failed: {e}")


def get_plugins_result() -> PluginsStartupResult | None:
    """Get the plugins startup result.

    Returns:
        PluginsStartupResult with discovery and lifecycle, or None if failed.
    """
    return _plugins_result
