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

"""Capability assembly for runtime-backed windows."""

from __future__ import annotations

from dataclasses import dataclass

from capabilities.connector_actions import ConnectorActions
from capabilities.connector_read import ConnectorRead
from capabilities.menu import MenuApi
from capabilities.plugin_read import PluginRead
from capabilities.plugin_selection import PluginSelectionActions, PluginSelectionApi
from capabilities.plugin_state_read import PluginStateRead
from capabilities.plugin_state_write import PluginStateWrite
from capabilities.settings_read import SettingsRead
from capabilities.settings_write import SettingsWrite
from capabilities.statusbar import StatusbarApi
from capabilities.tabs import TabsApi
from capabilities.widget_config_read import WidgetConfigRead
from capabilities.widget_config_write import WidgetConfigWrite
from capabilities.widget_read import WidgetRead
from capabilities.window_read import WindowRead
from runtime.runtime import Runtime
from runtime_schema import EventBus


@dataclass(frozen=True)
class SharedCapabilities:
    """Capabilities that can exist before runtime boot completes."""

    menus: object
    statusbar: object
    plugin_selection: object
    plugin_selection_actions: object
    tabs: object
    connector_read: object
    connector_actions: object


@dataclass(frozen=True)
class RuntimeCapabilities:
    """Capabilities that require booted runtime state."""

    plugin_read: object
    plugin_state: object
    plugin_state_write: object
    settings_read: object
    settings_write: object
    window_read: object
    widget_read: object
    widget_config_read: object
    widget_config_write: object


def create_shared_capabilities(event_bus: EventBus, runtime: Runtime) -> SharedCapabilities:
    """Create capabilities that do not need BOOT_INIT readiness."""

    return SharedCapabilities(
        menus=MenuApi(event_bus),
        statusbar=StatusbarApi(event_bus),
        plugin_selection=PluginSelectionApi(event_bus),
        plugin_selection_actions=PluginSelectionActions(event_bus),
        tabs=TabsApi(event_bus),
        connector_read=ConnectorRead(event_bus, runtime.connector_services),
        connector_actions=ConnectorActions(runtime.connector_services),
    )


def create_runtime_capabilities(runtime: Runtime, event_bus: EventBus) -> RuntimeCapabilities:
    """Create capabilities that require booted runtime state."""

    assert runtime.paths is not None, "Runtime capabilities require BOOT_INIT first"
    assert runtime.settings is not None, "Runtime capabilities require BOOT_INIT first"

    settings_read = SettingsRead(runtime)
    widget_config_read = WidgetConfigRead(runtime.widget_store)
    return RuntimeCapabilities(
        plugin_read=PluginRead(runtime),
        plugin_state=PluginStateRead(runtime, event_bus),
        plugin_state_write=PluginStateWrite(runtime),
        settings_read=settings_read,
        settings_write=SettingsWrite(runtime, settings_read),
        window_read=WindowRead(runtime, event_bus),
        widget_read=WidgetRead(runtime, event_bus),
        widget_config_read=widget_config_read,
        widget_config_write=WidgetConfigWrite(runtime.widget_store, widget_config_read),
    )


def build_window_capability_properties(
    manifest,
    shared: SharedCapabilities,
    runtime_caps: RuntimeCapabilities,
    runtime,  # For qml_capabilities()
    *,
    plugin_panel_url: str = "",
    plugin_panel_component: object | None = None,
) -> dict[str, object]:
    """Build the capability property bag for one hosted window."""

    properties: dict[str, object] = {
        "menus": shared.menus,
        "statusbar": shared.statusbar,
        "pluginSelection": shared.plugin_selection,
        "pluginSelectionActions": shared.plugin_selection_actions,
        "pluginState": runtime_caps.plugin_state,
        "pluginStateWrite": runtime_caps.plugin_state_write,
        "pluginRead": runtime_caps.plugin_read,
        "settingsRead": runtime_caps.settings_read,
        "settingsWrite": runtime_caps.settings_write,
        "windowRead": runtime_caps.window_read,
        "widgetRead": runtime_caps.widget_read,
        "widgetConfigRead": runtime_caps.widget_config_read,
        "widgetConfigWrite": runtime_caps.widget_config_write,
        "connectorRead": shared.connector_read,
        "connectorActions": shared.connector_actions,
    }

    # Add runtime capability QML interfaces
    for name, qml_iface in runtime.qml_capabilities().items():
        properties[name] = qml_iface

    if manifest.chrome.show_tab_bar:
        properties["tabs"] = shared.tabs
    if plugin_panel_url or plugin_panel_component is not None:
        properties["pluginPanelUrl"] = plugin_panel_url
        properties["pluginPanelComponent"] = plugin_panel_component
    return properties
