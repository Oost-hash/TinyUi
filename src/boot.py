"""TinyUI entry point — Qt setup only, all orchestration via events."""

from __future__ import annotations

from dataclasses import dataclass
import sys
from typing import Any, Protocol, Sequence

from app_schema.ui import AppManifest
from ui_api.api.app_actions import AppActions
from ui_api.qt import create_application, create_engine
from ui_api.theme import Theme
from ui_api.ui_runtime_host import WindowHostController, attach_main_window_shutdown, attach_window_runtime_tracking
from ui_api.window import open_window
from widget_api import create_widget_window_host
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
from capabilities.window_read import WindowRead
from capabilities.widget_read import WidgetRead
from PySide6.QtCore import QUrl
from PySide6.QtQml import QQmlComponent
from runtime.runtime import Runtime
from runtime.ui import WindowRuntimeRecord
from runtime.widgets import WidgetRuntimeRecord
from runtime_schema import EventBus, EventType, BootInitData, BootReadyData

if sys.platform == "win32":
    from ui_api.windowing import win_window  # noqa: F401  # eager import for Windows QML singletons


@dataclass(frozen=True)
class SharedCapabilities:
    menus: object
    statusbar: object
    plugin_selection: object
    plugin_selection_actions: object
    tabs: object
    connector_read: object
    connector_actions: object


@dataclass(frozen=True)
class RuntimeCapabilities:
    plugin_read: object
    plugin_state: object
    plugin_state_write: object
    settings_read: object
    settings_write: object
    window_read: object
    widget_read: object


class _WindowRuntimeLike(Protocol):
    def window_for(self, window_id: str) -> AppManifest | None: ...
    def all_windows(self) -> Sequence[AppManifest]: ...
    def window_records(self) -> Sequence[WindowRuntimeRecord]: ...
    def mark_window_opening(self, window_id: str) -> None: ...
    def mark_window_open(self, window_id: str) -> None: ...
    def mark_window_closing(self, window_id: str) -> None: ...
    def mark_window_closed(self, window_id: str) -> None: ...
    def mark_window_error(self, window_id: str, message: str) -> None: ...
    def begin_shutdown(self, reason: str = "app_quit") -> None: ...


def create_shared_capabilities(event_bus: EventBus, runtime: Runtime) -> SharedCapabilities:
    """Create capabilities that can exist before runtime boot completes."""
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
    return RuntimeCapabilities(
        plugin_read=PluginRead(runtime),
        plugin_state=PluginStateRead(runtime, event_bus),
        plugin_state_write=PluginStateWrite(runtime),
        settings_read=settings_read,
        settings_write=SettingsWrite(runtime, settings_read),
        window_read=WindowRead(runtime, event_bus),
        widget_read=WidgetRead(runtime, event_bus),
    )


def build_window_capability_properties(
    manifest,
    shared: SharedCapabilities,
    runtime_caps: RuntimeCapabilities,
    *,
    plugin_panel_url: str = "",
    plugin_panel_component: object | None = None,
) -> dict[str, object]:
    """Build the capability property bag for a window."""
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
        "connectorRead": shared.connector_read,
        "connectorActions": shared.connector_actions,
    }
    if manifest.chrome.show_tab_bar:
        properties["tabs"] = shared.tabs
    if plugin_panel_url or plugin_panel_component is not None:
        properties["pluginPanelUrl"] = plugin_panel_url
        properties["pluginPanelComponent"] = plugin_panel_component
    return properties


def emit_boot_init(event_bus: EventBus) -> None:
    """Emit the boot init event that prepares runtime state."""
    event_bus.emit_typed(EventType.BOOT_INIT, BootInitData(
        config_dir="",  # Runtime detects these via AppPaths
        plugins_dir="",
        data_dir="",
    ))


def emit_boot_ready(event_bus: EventBus, *, main_window_id: str) -> None:
    """Emit the boot ready event once the main window is known."""
    event_bus.emit_typed(EventType.BOOT_READY, BootReadyData(main_window_id=main_window_id))


def resolve_plugin_panel(engine, runtime: Runtime) -> tuple[str, object | None]:
    """Resolve the optional plugin panel component exposed to host windows."""
    assert runtime.paths is not None
    plugin_panel_path = runtime.paths.host_dir / "app_pluginsPanel" / "qml" / "surface.qml"
    if not plugin_panel_path.exists():
        return "", None
    plugin_panel_url = QUrl.fromLocalFile(str(plugin_panel_path))
    return str(plugin_panel_path), QQmlComponent(engine, plugin_panel_url)


def open_main_window(
    *,
    app,
    engine,
    actions: AppActions,
    theme: Theme,
    runtime: Runtime,
    shared_capabilities: SharedCapabilities,
    runtime_capabilities: RuntimeCapabilities,
):
    """Open the main host window with its boot-time capability bag."""
    main_manifest = runtime.main_window()
    if main_manifest is None:
        print("No main window found", file=sys.stderr)
        return None, None

    plugin_panel_url, plugin_panel_component = resolve_plugin_panel(engine, runtime)
    main_window_properties = build_window_capability_properties(
        main_manifest,
        shared_capabilities,
        runtime_capabilities,
        plugin_panel_url=plugin_panel_url,
        plugin_panel_component=plugin_panel_component,
    )
    runtime.mark_window_opening(main_manifest.id)
    try:
        handle = open_window(
            main_manifest,
            engine=engine,
            app=app,
            actions=actions,
            theme=theme,
            **main_window_properties,
        )
    except Exception as exc:
        runtime.mark_window_error(main_manifest.id, str(exc))
        raise
    runtime.mark_window_open(main_manifest.id)
    attach_window_runtime_tracking(runtime, main_manifest.id, handle.qml_window)
    attach_main_window_shutdown(runtime, handle.qml_window)
    return main_manifest, handle


def register_window_actions(
    *,
    app,
    engine,
    actions: AppActions,
    theme: Theme,
    runtime: _WindowRuntimeLike,
    shared_capabilities: SharedCapabilities,
    runtime_capabilities: RuntimeCapabilities,
    main_manifest,
    main_handle,
    window_host_controller: WindowHostController,
) -> None:
    """Register open and close actions after the main window exists."""
    main_handle.qml_window.destroyed.connect(app.quit)
    main_handle.qml_window.setProperty("showStatusBar", True)
    main_handle.qml_window.setProperty("showTabBar", True)
    window_host_controller.track(main_manifest.id, main_handle)

    open_handles = []

    def make_open_handler(window_id: str):
        def handler():
            manifest = runtime.window_for(window_id)
            if manifest is None:
                return
            kwargs = build_window_capability_properties(
                manifest,
                shared_capabilities,
                runtime_capabilities,
            )
            runtime.mark_window_opening(window_id)
            try:
                handle = open_window(manifest, engine=engine, app=app, actions=actions, theme=theme, **kwargs)
            except Exception as exc:
                runtime.mark_window_error(window_id, str(exc))
                raise
            runtime.mark_window_open(window_id)
            attach_window_runtime_tracking(runtime, window_id, handle.qml_window)
            window_host_controller.track(window_id, handle)
            open_handles.append(handle)
        return handler

    for window in runtime.all_windows():
        if window.id != main_manifest.id:
            actions.register(f"open:{window.id}", make_open_handler(window.id))

    def _close_main() -> None:
        runtime.begin_shutdown("main_window_close")
        main_handle.qml_window.close()

    actions.register("close", _close_main)


def main() -> int:
    app = create_application()
    engine = create_engine()
    event_bus = EventBus()
    runtime = Runtime(event_bus)
    theme = Theme("dark")
    actions = AppActions()
    shared_capabilities = create_shared_capabilities(event_bus, runtime)
    emit_boot_init(event_bus)
    runtime_capabilities = create_runtime_capabilities(runtime, event_bus)
    main_manifest, main_handle = open_main_window(
        app=app,
        engine=engine,
        actions=actions,
        theme=theme,
        runtime=runtime,
        shared_capabilities=shared_capabilities,
        runtime_capabilities=runtime_capabilities,
    )
    if main_manifest is None:
        return 1
    create_widget_window_host(app, event_bus, runtime)
    window_host_controller = WindowHostController(event_bus)
    window_host_controller.attach()
    app.aboutToQuit.connect(runtime.begin_shutdown)
    emit_boot_ready(event_bus, main_window_id=main_manifest.id)
    register_window_actions(
        app=app,
        engine=engine,
        actions=actions,
        theme=theme,
        runtime=runtime,
        shared_capabilities=shared_capabilities,
        runtime_capabilities=runtime_capabilities,
        main_manifest=main_manifest,
        main_handle=main_handle,
        window_host_controller=window_host_controller,
    )
    app.setProperty("_windowHostController", window_host_controller)
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
