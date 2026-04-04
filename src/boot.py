"""TinyUI entry point — Qt setup only, all orchestration via events."""

from __future__ import annotations

import sys

from app_api.api.app_actions import AppActions
from app_api.qt import create_application, create_engine
from app_api.theme import Theme
from app_api.window import open_window
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
from PySide6.QtCore import QUrl
from PySide6.QtQml import QQmlComponent
from runtime.runtime import Runtime
from runtime_schema import EventBus, EventType, BootInitData, BootReadyData

if sys.platform == "win32":
    from app_api.windowing import win_window  # noqa: F401  # eager import for Windows QML singletons


def main() -> int:
    # Create Qt application first
    app = create_application()
    engine = create_engine()
    
    # Create shared event bus — the only thing boot knows about
    event_bus = EventBus()
    
    # Create runtime — subscribes to events internally
    runtime = Runtime(event_bus)
    
    # Create theme and actions
    theme_name = "dark"  # Will be read from settings after boot
    theme = Theme(theme_name)
    actions = AppActions()
    
    # Create capability read/write models for QML
    menus = MenuApi(event_bus)
    statusbar = StatusbarApi(event_bus)
    plugin_selection = PluginSelectionApi(event_bus)
    plugin_selection_actions = PluginSelectionActions(event_bus)
    tabs = TabsApi(event_bus)
    connector_read = ConnectorRead(event_bus, runtime.providers)
    connector_actions = ConnectorActions(runtime.providers)
    
    # Emit boot init event — triggers initialization in all components
    event_bus.emit_typed(EventType.BOOT_INIT, BootInitData(
        config_dir="",  # Runtime detects these via AppPaths
        plugins_dir="",
        data_dir="",
    ))

    plugin_read = PluginRead(runtime)
    plugin_state = PluginStateRead(runtime, event_bus)
    plugin_state_write = PluginStateWrite(runtime)
    settings_read = SettingsRead(runtime)
    settings_write = SettingsWrite(runtime, settings_read)
    
    # Get main window (now available after BOOT_INIT)
    main_manifest = runtime.main_window()
    if main_manifest is None:
        print("No main window found", file=sys.stderr)
        return 1
    
    assert runtime.paths is not None
    
    # Emit boot ready
    event_bus.emit_typed(EventType.BOOT_READY, BootReadyData(
        main_window_id=main_manifest.id,
    ))
    
    # Open main window
    plugin_panel_component = None
    plugin_panel_path = runtime.paths.host_dir / "app_pluginsPanel" / "qml" / "surface.qml"
    if plugin_panel_path.exists():
        plugin_panel_url = QUrl.fromLocalFile(str(plugin_panel_path))
        plugin_panel_component = QQmlComponent(engine, plugin_panel_url)

    main_handle = open_window(
        main_manifest, 
        engine=engine, 
        app=app, 
        actions=actions, 
        theme=theme,
        menus=menus,
        statusbar=statusbar,
        pluginSelection=plugin_selection,
        pluginSelectionActions=plugin_selection_actions,
        pluginState=plugin_state,
        pluginStateWrite=plugin_state_write,
        pluginRead=plugin_read,
        settingsRead=settings_read,
        settingsWrite=settings_write,
        tabs=tabs,
        connectorRead=connector_read,
        connectorActions=connector_actions,
        pluginPanelUrl=str(plugin_panel_path) if plugin_panel_component else "",
        pluginPanelComponent=plugin_panel_component,
    )

    # When the main window is destroyed, terminate the whole application
    # even if auxiliary dialogs are still open.
    main_handle.qml_window.destroyed.connect(app.quit)
    
    # Enable UI features
    main_handle.qml_window.setProperty("showStatusBar", True)
    main_handle.qml_window.setProperty("showTabBar", True)
    
    # Register dialog handlers
    open_handles = []
    
    def make_open_handler(window_id: str, requires: list[str]):
        def handler():
            manifest = runtime.window_for(window_id)
            if manifest:
                kwargs = {}
                kwargs["menus"] = menus
                kwargs["statusbar"] = statusbar
                kwargs["pluginSelection"] = plugin_selection
                kwargs["pluginSelectionActions"] = plugin_selection_actions
                kwargs["pluginState"] = plugin_state
                kwargs["pluginStateWrite"] = plugin_state_write
                kwargs["pluginRead"] = plugin_read
                kwargs["settingsRead"] = settings_read
                kwargs["settingsWrite"] = settings_write
                kwargs["tabs"] = tabs
                kwargs["connectorRead"] = connector_read
                kwargs["connectorActions"] = connector_actions
                h = open_window(manifest, engine=engine, app=app, actions=actions, theme=theme, **kwargs)
                open_handles.append(h)
        return handler
    
    for w in runtime.all_windows():
        if w.id != main_manifest.id:
            actions.register(f"open:{w.id}", make_open_handler(w.id, w.requires))
    
    def close_main_window() -> None:
        main_handle.qml_window.close()

    actions.register("close", close_main_window)
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
