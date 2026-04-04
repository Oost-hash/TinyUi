"""Runtime schema definitions - runtime events, state, and settings."""

from runtime_schema.events import (
    BootInitData,
    BootReadyData,
    Event,
    EventBus,
    EventCallback,
    EventType,
    MenuRegisteredData,
    StatusbarRegisteredData,
    TabRegisteredData,
    UIPluginSelectedData,
)
from runtime_schema.plugin import (
    PluginActivatedData,
    PluginDeactivatedData,
    PluginErrorData,
    PluginState,
    PluginStateData,
)
from runtime_schema.provider import (
    ProviderRegisteredData,
    ProviderUnregisteredData,
    ProviderUpdatedData,
)
from runtime_schema.settings import SettingsSpec, VALID_SETTING_TYPES

__all__ = [
    # Events
    "BootInitData",
    "BootReadyData",
    "Event",
    "EventBus",
    "EventCallback",
    "EventType",
    "MenuRegisteredData",
    "StatusbarRegisteredData",
    "TabRegisteredData",
    "UIPluginSelectedData",
    # Plugin
    "PluginActivatedData",
    "PluginDeactivatedData",
    "PluginErrorData",
    "PluginState",
    "PluginStateData",
    # Provider
    "ProviderRegisteredData",
    "ProviderUnregisteredData",
    "ProviderUpdatedData",
    # Settings
    "SettingsSpec",
    "VALID_SETTING_TYPES",
]
