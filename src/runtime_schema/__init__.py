"""Runtime schema definitions - all runtime types in one place."""

from runtime_schema.context import PluginContext
from runtime_schema.events import (
    Event,
    EventBus,
    EventCallback,
    EventType,
    UIPluginSelectedData,
)
from runtime_schema.menu import MenuEntry, MenuItem, MenuSeparator
from runtime_schema.plugin import (
    PluginActivatedData,
    PluginDeactivatedData,
    PluginErrorData,
    PluginState,
    PluginStateData,
)
from runtime_schema.settings import SettingsSpec, VALID_SETTING_TYPES
from runtime_schema.statusbar import StatusbarItem

__all__ = [
    # Context
    "PluginContext",
    # Events
    "Event",
    "EventBus",
    "EventCallback",
    "EventType",
    "UIPluginSelectedData",
    # Menu
    "MenuEntry",
    "MenuItem",
    "MenuSeparator",
    # Plugin
    "PluginActivatedData",
    "PluginDeactivatedData",
    "PluginErrorData",
    "PluginState",
    "PluginStateData",
    # Settings
    "SettingsSpec",
    "VALID_SETTING_TYPES",
    # Statusbar
    "StatusbarItem",
]
