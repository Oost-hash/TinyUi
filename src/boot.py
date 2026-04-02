"""TinyUI entry point — Qt setup only, all orchestration via events."""

from __future__ import annotations

import sys

from app_api.host_actions import HostActions
from app_api.host_runtime import HostRuntimeBridge
from app_api.inspector import RuntimeInspector
from app_api.qt import create_application, create_engine
from app_api.theme import Theme
from app_api.window import open_window
from app_api.windowing import win_window  # eager import: registers QML singletons before engine
from runtime.runtime import Runtime
from runtime_schema import EventBus, EventType, BootInitData, BootReadyData


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
    
    # Emit boot ready
    event_bus.emit_typed(EventType.BOOT_READY, BootReadyData(
        main_window_id=main_manifest.id,
    ))
    
    # Open main window
    main_handle = open_window(
        main_manifest, 
        engine=engine, 
        app=app, 
        actions=actions, 
        theme=theme,
        inspector=inspector,
        hostRuntime=host_runtime
    )
    
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
                h = open_window(manifest, engine=engine, app=app, actions=actions, theme=theme, **kwargs)
                open_handles.append(h)
        return handler
    
    for w in runtime.all_windows():
        if w.window_type == "dialog":
            actions.register(f"open:{w.id}", make_open_handler(w.id, w.requires))
    
    actions.register("close", lambda: main_handle.qml_window.close())
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
