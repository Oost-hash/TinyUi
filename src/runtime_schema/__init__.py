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

"""Runtime schema definitions - runtime events, state, and settings."""

from runtime_schema.events import (
    BootInitData,
    BootReadyData,
    Event,
    EventBus,
    EventCallback,
    EventType,
    MenuRegisteredData,
    RuntimeShutdownData,
    StatusbarRegisteredData,
    TabRegisteredData,
    UIPluginSelectedData,
    WindowRuntimeUpdatedData,
    WidgetRuntimeUpdatedData,
)
from runtime_schema.plugin import (
    PluginActivatedData,
    PluginDeactivatedData,
    PluginErrorData,
    PluginState,
    PluginStateData,
)
from runtime_schema.connector_service import (
    ConnectorServiceRegisteredData,
    ConnectorServiceUnregisteredData,
    ConnectorServiceUpdatedData,
)
from runtime_schema.settings import SettingsSpec, VALID_SETTING_TYPES
from runtime_schema.startup import StartupResult, StartupStep, run_startup_pipeline, startup_error, startup_ok

__all__ = [
    # Events
    "BootInitData",
    "BootReadyData",
    "Event",
    "EventBus",
    "EventCallback",
    "EventType",
    "MenuRegisteredData",
    "RuntimeShutdownData",
    "StatusbarRegisteredData",
    "TabRegisteredData",
    "UIPluginSelectedData",
    "WindowRuntimeUpdatedData",
    "WidgetRuntimeUpdatedData",
    # Plugin
    "PluginActivatedData",
    "PluginDeactivatedData",
    "PluginErrorData",
    "PluginState",
    "PluginStateData",
    # Connector service
    "ConnectorServiceRegisteredData",
    "ConnectorServiceUnregisteredData",
    "ConnectorServiceUpdatedData",
    # Settings
    "SettingsSpec",
    "VALID_SETTING_TYPES",
    # Startup
    "StartupResult",
    "StartupStep",
    "run_startup_pipeline",
    "startup_error",
    "startup_ok",
]
