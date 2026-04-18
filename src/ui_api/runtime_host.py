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
from shared_runtime_host.events import SharedRuntimeHostEvents
from shared_runtime_host.registry import SharedRuntimeHostRegistry
from shared_runtime_host.shutdown import QmlRuntimeHostShutdown
from runtimeV2.capabilities.runtime_globals import RuntimeGlobals
from runtimeV2.contracts import (
    ConnectorReader,
    ConnectorWriter,
    MainWindowReader,
    ManifestReader,
    ManifestUiReader,
    PanelStateReader,
    PanelStateWriter,
    PluginActiveReader,
    PluginActiveWriter,
    PluginDiscovery,
    PluginIconResolver,
    PluginStateReader,
    PluginStateWriter,
    RenderStatusReader,
    SettingsReader,
    SettingsWriter,
    UIChromeModelReader,
    WidgetConfigReader,
    WidgetConfigWriter,
    WidgetRecordsReader,
    WidgetRecordsRefresher,
    WidgetVisibilityReader,
    WidgetVisibilityWriter,
    WindowActionsWriter,
    WindowRecordsReader,
)
from runtimeV2.schemas.startup import StartupResult, startup_error, startup_ok
from runtimeV2.runtime import RuntimeV2
from runtimeV2.ui.startup_shutdown.startup import UIStartupResult
from runtimeV2.paths.capabilities.path import PathCapability
from shared_runtime_host.capabilities.ui_api import (
    ConnectorReadQmlCapability,
    ConnectorWriteQmlCapability,
    ImageSourceQmlCapability,
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
    WidgetPreviewActions,
    WidgetRecordsQmlCapability,
    WidgetVisibilityQmlCapability,
)
from ui_api.api.app_actions import AppActions
from ui_api.startup_logging import log_startup_step
from ui_api.theme import Theme
from ui_api.window import WindowHandle, open_window


_QML_CAPABILITY_TYPES: dict[str, type[Any]] = {
    "manifest_read": ManifestReader,
    "settings_read": SettingsReader,
    "settings_write": SettingsWriter,
    "widget_config_read": WidgetConfigReader,
    "widget_config_write": WidgetConfigWriter,
    "connector_read": ConnectorReader,
    "connector_write": ConnectorWriter,
    "plugin_active_read": PluginActiveReader,
    "plugin_active_write": PluginActiveWriter,
    "plugin_state_read": PluginStateReader,
    "plugin_state_write": PluginStateWriter,
    "widget_records_read": WidgetRecordsReader,
    "widget_visibility_read": WidgetVisibilityReader,
    "widget_visibility_write": WidgetVisibilityWriter,
    "window_records_read": WindowRecordsReader,
    "panel_state_read": PanelStateReader,
    "window_actions_write": WindowActionsWriter,
    "render_status_read": RenderStatusReader,
    "ui_chrome_model_read": UIChromeModelReader,
}


@dataclass(frozen=True)
class RuntimeHostResult:
    """Live ui_api objects hosting runtime V2."""

    actions: AppActions
    theme: Theme
    main_handle: WindowHandle
    window_handles: dict[str, WindowHandle]
    qml_properties: dict[str, object]
    shutdown: QmlRuntimeHostShutdown


def build_runtime_qml_properties(
    runtime: RuntimeV2,
    ui_result: UIStartupResult,
    host_registry: SharedRuntimeHostRegistry,
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
    host_registry: SharedRuntimeHostRegistry,
    properties: dict[str, object],
) -> dict[str, object]:
    """Defensively normalize host properties to QML-facing wrappers."""

    connector_actions = properties.get("connectorActions")
    if isinstance(connector_actions, ConnectorWriter):
        properties["connectorActions"] = ConnectorWriteQmlCapability(connector_actions)

    connector_read = properties.get("connectorRead")
    if isinstance(connector_read, ConnectorReader):
        host_events = host_registry.capability("event_registration", SharedRuntimeHostEvents)
        properties["connectorRead"] = ConnectorReadQmlCapability(
            connector_read,
            host_events,
        )

    settings_read = properties.get("settingsRead")
    if isinstance(settings_read, SettingsReader):
        properties["settingsRead"] = SettingsQmlCapability(settings_read)

    manifest_read = properties.get("manifestRead")
    if isinstance(manifest_read, ManifestReader):
        properties["manifestRead"] = ManifestQmlCapability(
            manifest_read,
            runtime.capability("plugin_icon", PluginIconResolver),
        )

    plugin_state = properties.get("pluginState")
    if isinstance(plugin_state, PluginStateReader):
        discovery = runtime.capability("plugin_discovery", PluginDiscovery)
        host_events = host_registry.capability("event_registration", SharedRuntimeHostEvents)
        properties["pluginState"] = PluginStateQmlCapability(
            plugin_state,
            discovery.plugin_ids(),
            host_events,
        )

    if "widgetPreviewActions" not in properties and host_registry.has_capability("widget_preview_actions"):
        properties["widgetPreviewActions"] = host_registry.capability("widget_preview_actions", WidgetPreviewActions)

    if "imageSources" not in properties and runtime.try_capability("paths") is not None:
        properties["imageSources"] = ImageSourceQmlCapability(
            runtime.capability("paths", PathCapability),
        )

    return properties


def _adapt_qml_property(
    runtime: RuntimeV2,
    host_registry: SharedRuntimeHostRegistry,
    capability_name: str,
    capability: object,
) -> object:
    """Adapt selected runtime V2 capabilities to QML-facing objects."""

    if capability_name == "ui_chrome_model_read":
        return UIChromeQmlCapability(host_registry.capability("ui_host", UIHostCapability))
    if capability_name == "manifest_read":
        return ManifestQmlCapability(
            cast(ManifestReader, capability),
            runtime.capability("plugin_icon", PluginIconResolver),
        )
    if capability_name == "settings_read":
        return SettingsQmlCapability(cast(SettingsReader, capability))
    if capability_name == "settings_write":
        return SettingsWriteQmlCapability(cast(SettingsWriter, capability))
    if capability_name == "connector_read":
        host_events = host_registry.capability("event_registration", SharedRuntimeHostEvents)
        return ConnectorReadQmlCapability(
            cast(ConnectorReader, capability),
            host_events,
        )
    if capability_name == "connector_write":
        return ConnectorWriteQmlCapability(cast(ConnectorWriter, capability))
    if capability_name == "widget_config_read":
        return WidgetConfigReadQmlCapability(cast(WidgetConfigReader, capability))
    if capability_name == "widget_config_write":
        records_refresh = runtime.try_capability("widget_records_refresh")
        return WidgetConfigWriteQmlCapability(
            cast(WidgetConfigWriter, capability),
            cast(WidgetRecordsRefresher, records_refresh) if records_refresh is not None else None,
        )
    if capability_name == "widget_records_read":
        host_events = host_registry.capability("event_registration", SharedRuntimeHostEvents)
        return WidgetRecordsQmlCapability(
            host_registry.capability("widget_host", WidgetHostCapability),
            host_events,
        )
    if capability_name == "window_records_read":
        return WindowRecordsQmlCapability(host_registry.capability("window_host", WindowHostCapability))
    if capability_name == "widget_visibility_read":
        host_events = host_registry.capability("event_registration", SharedRuntimeHostEvents)
        return WidgetVisibilityQmlCapability(
            cast(WidgetVisibilityReader, capability),
            runtime.capability("widget_visibility_write", WidgetVisibilityWriter),
            host_events,
        )
    if capability_name == "plugin_active_read":
        globals_capability = runtime.capability("globals", RuntimeGlobals)
        host_events = host_registry.capability("event_registration", SharedRuntimeHostEvents)
        return PluginActiveQmlCapability(
            globals_capability.read_global("active_plugin", PluginActiveReader),
            globals_capability.write_global("active_plugin", PluginActiveWriter),
            host_events,
        )
    if capability_name == "plugin_state_read":
        discovery = runtime.capability("plugin_discovery", PluginDiscovery)
        host_events = host_registry.capability("event_registration", SharedRuntimeHostEvents)
        return PluginStateQmlCapability(
            cast(PluginStateReader, capability),
            discovery.plugin_ids(),
            host_events,
        )
    if capability_name == "panel_state_read":
        host_events = host_registry.capability("event_registration", SharedRuntimeHostEvents)
        return PanelStateQmlCapability(
            cast(PanelStateReader, capability),
            runtime.capability("panel_state_write", PanelStateWriter),
            host_events,
        )
    if capability_name == "render_status_read":
        return RenderStatusQmlCapability(cast(RenderStatusReader, capability))
    return capability


def start_runtime_host(
    *,
    app,
    engine,
    runtime: RuntimeV2,
    host_registry: SharedRuntimeHostRegistry,
    theme: Theme | None = None,
) -> tuple[RuntimeHostResult | None, StartupResult]:
    """Open the runtime V2 main window through ui_api."""

    try:
        log_startup_step("runtime host startup begin")
        ui_result = runtime.domain_result("ui", UIStartupResult)
        if not ui_result.render_status.render_ready:
            blocker = ui_result.render_status.render_blocker or "unknown blocker"
            log_startup_step(f"runtime host blocked: {blocker}", level=40)
            return None, startup_error(f"Runtime V2 UI is not render-ready: {blocker}")

        if theme is None:
            theme = Theme("dark")

        actions = AppActions()
        main_window = runtime.capability("main_window_read", MainWindowReader).main_window()
        plugin_panel_url, plugin_panel_component = _resolve_plugin_panel(engine, runtime)
        qml_properties = _normalize_qml_properties(
            runtime,
            host_registry,
            build_runtime_qml_properties(runtime, ui_result, host_registry),
        )
        if plugin_panel_url:
            qml_properties["pluginPanelUrl"] = plugin_panel_url
        if plugin_panel_component is not None:
            qml_properties["pluginPanelComponent"] = plugin_panel_component
        log_startup_step(f"opening main runtime window: {main_window.id}")
        handle = open_window(
            main_window,
            engine=engine,
            app=app,
            actions=actions,
            theme=theme,
            isMainWindow=True,
            **qml_properties,
        )
        open_handles: dict[str, WindowHandle] = {main_window.id: handle}
        manifest_ui_read = runtime.capability("manifest_ui_read", ManifestUiReader)

        def _drop_handle(window_id: str) -> None:
            open_handles.pop(window_id, None)

        def _close_host_windows() -> None:
            for window_id, window_handle in list(open_handles.items()):
                if window_handle.qml_window is not None:
                    window_handle.qml_window.close()
                open_handles.pop(window_id, None)

        def _open_runtime_window(window_id: str) -> None:
            log_startup_step(f"requested runtime window: {window_id}")
            existing = open_handles.get(window_id)
            if existing is not None:
                if not existing.qml_window.isVisible():
                    _drop_handle(window_id)
                else:
                    existing.qml_window.raise_()
                    existing.qml_window.requestActivate()
                    return
            manifest = _window_manifest(manifest_ui_read, window_id)
            if manifest is None:
                return
            window_handle = open_window(
                manifest,
                engine=engine,
                app=app,
                actions=actions,
                theme=theme,
                isMainWindow=False,
                **qml_properties,
            )
            open_handles[window_id] = window_handle
            window_handle.qml_window.destroyed.connect(lambda *_args, wid=window_id: _drop_handle(wid))

        host_registry.capability("ui_actions", UIActionsCapability).register(
            actions,
            open_window=_open_runtime_window,
        )
        handle.qml_window.destroyed.connect(app.quit)
        handle.qml_window.destroyed.connect(lambda *_args: _drop_handle(main_window.id))
        shutdown = QmlRuntimeHostShutdown(runtime, _close_host_windows)
        shutdown.attach(app)

        result = RuntimeHostResult(
            actions=actions,
            theme=theme,
            main_handle=handle,
            window_handles=open_handles,
            qml_properties=qml_properties,
            shutdown=shutdown,
        )
        app.setProperty("_runtimeV2Host", result)
        log_startup_step("runtime host startup completed")
        return result, startup_ok()
    except Exception as exc:
        log_startup_step(f"runtime host startup exception: {exc}", level=40, exc_info=True)
        return None, startup_error(f"Runtime V2 ui_api host startup failed: {exc}")


def _window_manifest(ui_read: ManifestUiReader, window_id: str):
    """Resolve one manifest window by id."""

    for windows in ui_read.windows().values():
        for window in windows:
            if window.id == window_id:
                return window
    return None


def _resolve_plugin_panel(engine, runtime: RuntimeV2) -> tuple[str, QQmlComponent | None]:
    """Resolve the optional inline plugin panel component for the main host window."""

    ui_read = runtime.capability("manifest_ui_read", ManifestUiReader)
    panel_manifest = _window_manifest(ui_read, "pluginsPanel.main")
    if panel_manifest is None or panel_manifest.surface is None:
        return "", None

    panel_path = Path(panel_manifest.surface)
    if not panel_path.exists():
        return "", None

    panel_url = QUrl.fromLocalFile(str(panel_path))
    return panel_url.toString(), QQmlComponent(engine, panel_url)
