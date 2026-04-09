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
from pathlib import Path
from typing import Any, cast

from PySide6.QtCore import QUrl
from PySide6.QtQml import QQmlComponent

from shared_runtime_host.capabilities.ui_host import UIHostCapability
from shared_runtime_host.capabilities.window_host import WindowHostCapability
from shared_runtime_host.capabilities.widget_host import WidgetHostCapability
from shared_runtime_host.registry import SharedRuntimeHostRegistry, create_shared_runtime_host_registry
from shared_runtime_host.shutdown import QmlRuntimeHostShutdown
from runtimeV2.capabilities.runtime_globals import RuntimeGlobals
from runtimeV2.schemas.startup import StartupResult, startup_error, startup_ok
from runtimeV2.connectors.capabilities.connector_read import ConnectorRead
from runtimeV2.connectors.capabilities.connector_write import ConnectorWrite
from runtimeV2.host.capabilities.main_window_read import MainWindowRead
from runtimeV2.manifest.capabilities.manifest_read import ManifestRead
from runtimeV2.manifest.capabilities.ui_read import ManifestUiRead
from runtimeV2.persistence.capabilities.settings_read import SettingsRead
from runtimeV2.persistence.capabilities.settings_write import SettingsWrite
from runtimeV2.persistence.capabilities.widget_config_read import WidgetConfigRead
from runtimeV2.persistence.capabilities.widget_config_write import WidgetConfigWrite
from runtimeV2.plugins.capabilities.active_read import PluginActiveRead
from runtimeV2.plugins.capabilities.active_write import PluginActiveWrite
from runtimeV2.plugins.capabilities.discovery import PluginDiscoveryCapability
from runtimeV2.plugins.capabilities.icon import PluginIconCapability
from runtimeV2.plugins.capabilities.state_read import PluginStateRead
from runtimeV2.plugins.capabilities.state_write import PluginStateWrite
from runtimeV2.ui.capabilities.chrome_model_read import UIChromeModelRead
from runtimeV2.ui.capabilities.panel_state_read import PanelStateRead
from runtimeV2.ui.capabilities.panel_state_write import PanelStateWrite
from runtimeV2.runtime import RuntimeV2
from runtimeV2.ui.capabilities.window_actions_write import WindowActionsWrite
from runtimeV2.ui.capabilities.render_status_read import RenderStatusRead
from runtimeV2.ui.capabilities.window_records_read import WindowRecordsRead
from runtimeV2.events.startup_shutdown.startup import EventsStartupResult
from runtimeV2.ui.startup_shutdown.startup import UIStartupResult
from runtimeV2.widgets.capabilities.widget_records_read import WidgetRecordsRead
from runtimeV2.widgets.capabilities.widget_visibility_read import WidgetVisibilityRead
from runtimeV2.widgets.capabilities.widget_visibility_write import WidgetVisibilityWrite
from shared_runtime_host.capabilities.ui_api import (
    ConnectorReadQmlCapability,
    ConnectorWriteQmlCapability,
    ManifestQmlCapability,
    PanelStateQmlCapability,
    PluginActiveQmlCapability,
    PluginStateQmlCapability,
    RenderStatusQmlCapability,
    SettingsQmlCapability,
    SettingsWriteQmlCapability,
    UIActionsCapability,
    UIChromeQmlCapability,
    WindowRecordsQmlCapability,
    WidgetConfigReadQmlCapability,
    WidgetConfigWriteQmlCapability,
    WidgetRecordsQmlCapability,
    WidgetVisibilityQmlCapability,
)
from ui_api.api.app_actions import AppActions
from ui_api.register_runtime_host import register_ui_runtime_host
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
    "panel_state_read": PanelStateRead,
    "window_actions_write": WindowActionsWrite,
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
    shutdown: QmlRuntimeHostShutdown


def build_runtime_qml_properties(
    runtime: RuntimeV2,
    ui_result: UIStartupResult,
    host_registry: SharedRuntimeHostRegistry | None = None,
) -> dict[str, object]:
    """Build QML properties from the runtime V2 UI property schema."""

    properties: dict[str, object] = {}
    for item in ui_result.qml_property_plan:
        capability_type = _QML_CAPABILITY_TYPES.get(item.capability_name)
        if capability_type is None:
            raise KeyError(f"Runtime V2 QML property has no ui_api host type: {item.capability_name}")
        capability = runtime.capability(item.capability_name, capability_type)
        properties[item.qml_property] = _adapt_qml_property(
            runtime,
            host_registry,
            item.capability_name,
            capability,
        )
    return properties


def _normalize_qml_properties(
    runtime: RuntimeV2,
    properties: dict[str, object],
) -> dict[str, object]:
    """Defensively normalize host properties to QML-facing wrappers."""

    connector_actions = properties.get("connectorActions")
    if isinstance(connector_actions, ConnectorWrite):
        properties["connectorActions"] = ConnectorWriteQmlCapability(connector_actions)

    connector_read = properties.get("connectorRead")
    if isinstance(connector_read, ConnectorRead):
        properties["connectorRead"] = ConnectorReadQmlCapability(connector_read)

    settings_read = properties.get("settingsRead")
    if isinstance(settings_read, SettingsRead):
        properties["settingsRead"] = SettingsQmlCapability(settings_read)

    manifest_read = properties.get("manifestRead")
    if isinstance(manifest_read, ManifestRead):
        properties["manifestRead"] = ManifestQmlCapability(
            manifest_read,
            runtime.capability("plugin_icon", PluginIconCapability),
        )

    plugin_state = properties.get("pluginState")
    if isinstance(plugin_state, PluginStateRead):
        discovery = runtime.capability("plugin_discovery", PluginDiscoveryCapability)
        events = runtime.domain_result("events", EventsStartupResult)
        properties["pluginState"] = PluginStateQmlCapability(
            plugin_state,
            discovery.plugin_ids(),
            events,
        )

    return properties


def _adapt_qml_property(
    runtime: RuntimeV2,
    host_registry: SharedRuntimeHostRegistry | None,
    capability_name: str,
    capability: object,
) -> object:
    """Adapt selected runtime V2 capabilities to QML-facing objects."""

    if capability_name == "ui_chrome_model_read":
        if host_registry is None:
            host_registry = create_shared_runtime_host_registry(runtime)
            register_ui_runtime_host(host_registry)
        return UIChromeQmlCapability(host_registry.capability("ui_host", UIHostCapability))
    if capability_name == "manifest_read":
        return ManifestQmlCapability(
            cast(ManifestRead, capability),
            runtime.capability("plugin_icon", PluginIconCapability),
        )
    if capability_name == "settings_read":
        return SettingsQmlCapability(cast(SettingsRead, capability))
    if capability_name == "settings_write":
        return SettingsWriteQmlCapability(cast(SettingsWrite, capability))
    if capability_name == "connector_read":
        return ConnectorReadQmlCapability(cast(ConnectorRead, capability))
    if capability_name == "connector_write":
        return ConnectorWriteQmlCapability(cast(ConnectorWrite, capability))
    if capability_name == "widget_config_read":
        return WidgetConfigReadQmlCapability(cast(WidgetConfigRead, capability))
    if capability_name == "widget_config_write":
        return WidgetConfigWriteQmlCapability(cast(WidgetConfigWrite, capability))
    if capability_name == "widget_records_read":
        if host_registry is None:
            host_registry = create_shared_runtime_host_registry(runtime)
            register_ui_runtime_host(host_registry)
        return WidgetRecordsQmlCapability(
            host_registry.capability("widget_host", WidgetHostCapability),
            runtime.domain_result("events", EventsStartupResult),
        )
    if capability_name == "window_records_read":
        if host_registry is None:
            host_registry = create_shared_runtime_host_registry(runtime)
            register_ui_runtime_host(host_registry)
        return WindowRecordsQmlCapability(host_registry.capability("window_host", WindowHostCapability))
    if capability_name == "widget_visibility_read":
        return WidgetVisibilityQmlCapability(
            cast(WidgetVisibilityRead, capability),
            runtime.capability("widget_visibility_write", WidgetVisibilityWrite),
            runtime.domain_result("events", EventsStartupResult),
        )
    if capability_name == "plugin_active_read":
        globals_capability = runtime.capability("globals", RuntimeGlobals)
        return PluginActiveQmlCapability(
            globals_capability.read_global("active_plugin", PluginActiveRead),
            globals_capability.write_global("active_plugin", PluginActiveWrite),
            runtime.domain_result("events", EventsStartupResult),
        )
    if capability_name == "plugin_state_read":
        discovery = runtime.capability("plugin_discovery", PluginDiscoveryCapability)
        return PluginStateQmlCapability(
            cast(PluginStateRead, capability),
            discovery.plugin_ids(),
            runtime.domain_result("events", EventsStartupResult),
        )
    if capability_name == "panel_state_read":
        return PanelStateQmlCapability(
            cast(PanelStateRead, capability),
            runtime.capability("panel_state_write", PanelStateWrite),
            runtime.domain_result("events", EventsStartupResult),
        )
    if capability_name == "render_status_read":
        return RenderStatusQmlCapability(cast(RenderStatusRead, capability))
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

        host_registry = create_shared_runtime_host_registry(runtime)
        register_ui_runtime_host(host_registry)
        actions = AppActions()
        main_window = runtime.capability("main_window_read", MainWindowRead).main_window()
        plugin_panel_url, plugin_panel_component = _resolve_plugin_panel(engine, runtime)
        qml_properties = _normalize_qml_properties(
            runtime,
            build_runtime_qml_properties(runtime, ui_result, host_registry),
        )
        if plugin_panel_url:
            qml_properties["pluginPanelUrl"] = plugin_panel_url
        if plugin_panel_component is not None:
            qml_properties["pluginPanelComponent"] = plugin_panel_component
        handle = open_window(
            main_window,
            engine=engine,
            app=app,
            actions=actions,
            theme=theme,
            **qml_properties,
        )
        manifest_ui_read = runtime.capability("manifest_ui_read", ManifestUiRead)

        def _close_main_window() -> None:
            handle.qml_window.close()

        def _open_runtime_window(window_id: str) -> None:
            manifest = _window_manifest(manifest_ui_read, window_id)
            if manifest is None:
                return
            open_window(
                manifest,
                engine=engine,
                app=app,
                actions=actions,
                theme=theme,
                **qml_properties,
            )

        host_registry.capability("ui_actions", UIActionsCapability).register(
            actions,
            open_window=_open_runtime_window,
        )
        handle.qml_window.destroyed.connect(app.quit)
        shutdown = QmlRuntimeHostShutdown(runtime, _close_main_window)
        shutdown.attach(app)

        result = RuntimeHostResult(
            actions=actions,
            theme=theme,
            main_handle=handle,
            qml_properties=qml_properties,
            shutdown=shutdown,
        )
        app.setProperty("_runtimeV2Host", result)
        return result, startup_ok()
    except Exception as exc:
        return None, startup_error(f"Runtime V2 ui_api host startup failed: {exc}")


def _window_manifest(ui_read: ManifestUiRead, window_id: str):
    """Resolve one manifest window by id."""

    for windows in ui_read.windows().values():
        for window in windows:
            if window.id == window_id:
                return window
    return None


def _resolve_plugin_panel(engine, runtime: RuntimeV2) -> tuple[str, QQmlComponent | None]:
    """Resolve the optional inline plugin panel component for the main host window."""

    ui_read = runtime.capability("manifest_ui_read", ManifestUiRead)
    panel_manifest = _window_manifest(ui_read, "pluginsPanel.main")
    if panel_manifest is None or panel_manifest.surface is None:
        return "", None

    panel_path = Path(panel_manifest.surface)
    if not panel_path.exists():
        return "", None

    panel_url = QUrl.fromLocalFile(str(panel_path))
    return panel_url.toString(), QQmlComponent(engine, panel_url)

