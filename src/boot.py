"""TinyUI entry point — Qt setup only, all orchestration via events."""

from __future__ import annotations

import sys

from app_api.host_actions import HostActions
from app_api.host_runtime import HostRuntimeBridge
from app_api.inspector import RuntimeInspector
from app_api.provider_hub import ProviderHubBridge
from app_api.qt import create_application, create_engine
from app_api.theme import Theme
from app_api.window import open_window
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
    actions = HostActions()
    
    # Create bridge — subscribes to events and exposes Qt signals to QML
    host_runtime = HostRuntimeBridge(event_bus)
    provider_hub = ProviderHubBridge(event_bus, runtime.providers)
    
    # Inspector for devtools
    from app_schema.manifest import DevToolsData
    inspector = RuntimeInspector(DevToolsData(plugins=[], settings=[]))
    
    # Emit boot init event — triggers initialization in all components
    event_bus.emit_typed(EventType.BOOT_INIT, BootInitData(
        config_dir="",  # Runtime detects these via AppPaths
        plugins_dir="",
        data_dir="",
    ))
    
    # Get main window (now available after BOOT_INIT)
    main_manifest = runtime.main_window()
    if main_manifest is None:
        print("No main window found", file=sys.stderr)
        return 1
    
    # Update inspector with runtime data
    inspector.update_data(runtime.devtools_data())
    assert runtime.paths is not None

    # Keep inspector in sync when plugin states change (devtool stays live)
    event_bus.on(EventType.PLUGIN_STATE_CHANGED, lambda _: inspector.update_data(runtime.devtools_data()))
    event_bus.on(EventType.PLUGIN_ACTIVATED, lambda _: inspector.update_data(runtime.devtools_data()))
    
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
        inspector=inspector,
        hostRuntime=host_runtime,
        providerHub=provider_hub,
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
                if "inspector" in requires:
                    kwargs["inspector"] = inspector
                kwargs["providerHub"] = provider_hub
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
