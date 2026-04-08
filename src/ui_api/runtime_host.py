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

"""ui_api host for runtime V2."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, cast

from runtimeV2.schemas.startup import StartupResult, startup_error, startup_ok
from runtimeV2.connectors.capabilities.connector_read import ConnectorRead
from runtimeV2.connectors.capabilities.connector_write import ConnectorWrite
from runtimeV2.host.capabilities.main_window_read import MainWindowRead
from runtimeV2.manifest.capabilities.manifest_read import ManifestRead
from runtimeV2.persistence.capabilities.settings_read import SettingsRead
from runtimeV2.persistence.capabilities.settings_write import SettingsWrite
from runtimeV2.persistence.capabilities.widget_config_read import WidgetConfigRead
from runtimeV2.persistence.capabilities.widget_config_write import WidgetConfigWrite
from runtimeV2.plugins.capabilities.active_read import PluginActiveRead
from runtimeV2.plugins.capabilities.active_write import PluginActiveWrite
from runtimeV2.plugins.capabilities.discovery import PluginDiscoveryCapability
from runtimeV2.plugins.capabilities.state_read import PluginStateRead
from runtimeV2.plugins.capabilities.state_write import PluginStateWrite
from runtimeV2.ui.capabilities.chrome_model_read import UIChromeModelRead
from runtimeV2.runtime import RuntimeV2
from runtimeV2.ui.capabilities.render_status_read import RenderStatusRead
from runtimeV2.ui.capabilities.window_records_read import WindowRecordsRead
from runtimeV2.ui.startup import UIStartupResult
from runtimeV2.widgets.capabilities.widget_records_read import WidgetRecordsRead
from runtimeV2.widgets.capabilities.widget_visibility_read import WidgetVisibilityRead
from runtimeV2.widgets.capabilities.widget_visibility_write import WidgetVisibilityWrite
from ui_api.api.app_actions import AppActions
from ui_api.runtime_adapters import (
    ManifestQmlAdapter,
    PluginActiveQmlAdapter,
    PluginStateQmlAdapter,
    UIChromeQmlAdapter,
    WindowRecordsQmlAdapter,
    WidgetRecordsQmlAdapter,
    WidgetVisibilityQmlAdapter,
)
from ui_api.theme import Theme
from ui_api.window import WindowHandle, open_window


_QML_CAPABILITY_TYPES: dict[str, type[Any]] = {
    "manifest_read": ManifestRead,
    "settings_read": SettingsRead,
    "settings_write": SettingsWrite,
    "widget_config_read": WidgetConfigRead,
    "widget_config_write": WidgetConfigWrite,
    "connector_read": ConnectorRead,
    "connector_write": ConnectorWrite,
    "plugin_active_read": PluginActiveRead,
    "plugin_active_write": PluginActiveWrite,
    "plugin_state_read": PluginStateRead,
    "plugin_state_write": PluginStateWrite,
    "widget_records_read": WidgetRecordsRead,
    "widget_visibility_read": WidgetVisibilityRead,
    "widget_visibility_write": WidgetVisibilityWrite,
    "window_records_read": WindowRecordsRead,
    "render_status_read": RenderStatusRead,
    "ui_chrome_model_read": UIChromeModelRead,
}


@dataclass(frozen=True)
class RuntimeHostResult:
    """Live ui_api objects hosting runtime V2."""

    actions: AppActions
    theme: Theme
    main_handle: WindowHandle
    qml_properties: dict[str, object]


def build_runtime_qml_properties(runtime: RuntimeV2, ui_result: UIStartupResult) -> dict[str, object]:
    """Build QML properties from the runtime V2 UI property schema."""

    properties: dict[str, object] = {}
    for item in ui_result.qml_property_plan:
        capability_type = _QML_CAPABILITY_TYPES.get(item.capability_name)
        if capability_type is None:
            raise KeyError(f"Runtime V2 QML property has no ui_api host type: {item.capability_name}")
        capability = runtime.capability(item.capability_name, capability_type)
        properties[item.qml_property] = _adapt_qml_property(runtime, item.capability_name, capability)
    return properties


def _adapt_qml_property(runtime: RuntimeV2, capability_name: str, capability: object) -> object:
    """Adapt selected runtime V2 capabilities to QML-facing objects."""

    if capability_name == "ui_chrome_model_read":
        return UIChromeQmlAdapter(cast(UIChromeModelRead, capability))
    if capability_name == "manifest_read":
        return ManifestQmlAdapter(cast(ManifestRead, capability))
    if capability_name == "widget_records_read":
        return WidgetRecordsQmlAdapter(cast(WidgetRecordsRead, capability))
    if capability_name == "window_records_read":
        return WindowRecordsQmlAdapter(cast(WindowRecordsRead, capability))
    if capability_name == "widget_visibility_read":
        return WidgetVisibilityQmlAdapter(
            cast(WidgetVisibilityRead, capability),
            runtime.capability("widget_visibility_write", WidgetVisibilityWrite),
        )
    if capability_name == "plugin_active_read":
        return PluginActiveQmlAdapter(
            cast(PluginActiveRead, capability),
            runtime.capability("plugin_active_write", PluginActiveWrite),
        )
    if capability_name == "plugin_state_read":
        discovery = runtime.capability("plugin_discovery", PluginDiscoveryCapability)
        return PluginStateQmlAdapter(
            cast(PluginStateRead, capability),
            discovery.plugin_ids(),
        )
    return capability


def start_runtime_host(
    *,
    app,
    engine,
    runtime: RuntimeV2,
    theme: Theme | None = None,
) -> tuple[RuntimeHostResult | None, StartupResult]:
    """Open the runtime V2 main window through ui_api."""

    try:
        ui_result = runtime.domain_result("ui", UIStartupResult)
        if not ui_result.render_status.render_ready:
            blocker = ui_result.render_status.render_blocker or "unknown blocker"
            return None, startup_error(f"Runtime V2 UI is not render-ready: {blocker}")

        if theme is None:
            theme = Theme("dark")

        actions = AppActions()
        main_window = runtime.capability("main_window_read", MainWindowRead).main_window()
        qml_properties = build_runtime_qml_properties(runtime, ui_result)
        handle = open_window(
            main_window,
            engine=engine,
            app=app,
            actions=actions,
            theme=theme,
            **qml_properties,
        )
        def _close_main_window() -> None:
            handle.qml_window.close()

        actions.register("close", _close_main_window)
        handle.qml_window.destroyed.connect(app.quit)

        result = RuntimeHostResult(
            actions=actions,
            theme=theme,
            main_handle=handle,
            qml_properties=qml_properties,
        )
        app.setProperty("_runtimeV2Host", result)
        return result, startup_ok()
    except Exception as exc:
        return None, startup_error(f"Runtime V2 ui_api host startup failed: {exc}")
