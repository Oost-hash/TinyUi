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
