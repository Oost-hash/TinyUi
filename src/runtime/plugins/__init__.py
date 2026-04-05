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

"""Plugin runtime helpers and lifecycle primitives."""

from runtime.plugins.contracts import PluginContext
from runtime.plugins.discovery import PluginDiscovery
from runtime.plugins.lifecycle_manager import PluginLifecycleManager
from runtime.plugins.plugin_lifecycle import (
    NoOpPluginLifecycle,
    PluginLifecycle,
    PythonModulePluginLifecycle,
    resolve_plugin_lifecycle,
)
from runtime.plugins.plugin_state import PluginStateMachine, StateTransition
from runtime.plugins.startup import PluginsStartupResult, get_plugins_result, startup_plugins

__all__ = [
    "NoOpPluginLifecycle",
    "PluginContext",
    "PluginDiscovery",
    "PluginLifecycle",
    "PluginLifecycleManager",
    "PluginStateMachine",
    "PluginsStartupResult",
    "PythonModulePluginLifecycle",
    "StateTransition",
    "get_plugins_result",
    "resolve_plugin_lifecycle",
    "startup_plugins",
]
