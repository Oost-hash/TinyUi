"""TinyUI entry point — Qt setup only, all orchestration via events."""

from __future__ import annotations

import sys
from typing import cast

from app_schema.ui import AppManifest
from ui_api.api.app_actions import AppActions
from ui_api.qt import create_application, create_engine
from ui_api.startup import open_main_runtime_window, register_runtime_window_actions
from ui_api.theme import Theme
from ui_api.ui_runtime_host import WindowHostController, start_window_host
from widget_api import start_widget_host
from capabilities.window_capabilities import (
    build_window_capability_properties,
    create_runtime_capabilities,
    create_shared_capabilities,
)
from runtime.runtime import Runtime
from runtime.ui import start_runtime_ui
from runtime.widgets import start_runtime_widgets
from runtime_schema import EventBus, EventType, BootInitData, BootReadyData, StartupStep, run_startup_pipeline

if sys.platform == "win32":
    from ui_api.windowing import win_window  # noqa: F401  # eager import for Windows QML singletons


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
    startup_context: dict[str, object] = {}

    def _start_runtime_ui():
        return start_runtime_ui(runtime)

    def _start_window_host():
        controller, result = start_window_host(event_bus)
        startup_context["window_host_controller"] = controller
        return result

    def _open_main_window():
        main_manifest, main_handle, result = open_main_runtime_window(
            app=app,
            engine=engine,
            actions=actions,
            theme=theme,
            runtime=runtime,
            shared_capabilities=shared_capabilities,
            runtime_capabilities=runtime_capabilities,
            build_window_capability_properties=build_window_capability_properties,
        )
        startup_context["main_manifest"] = main_manifest
        startup_context["main_handle"] = main_handle
        return result

    def _start_runtime_widgets():
        return start_runtime_widgets(runtime)

    def _start_widget_host():
        widget_host, result = start_widget_host(app, event_bus, runtime)
        startup_context["widget_host"] = widget_host
        return result

    startup_result = run_startup_pipeline([
        StartupStep("runtime_ui", _start_runtime_ui),
        StartupStep("window_host", _start_window_host),
        StartupStep("main_window", _open_main_window),
        StartupStep("runtime_widgets", _start_runtime_widgets),
        StartupStep("widget_host", _start_widget_host),
    ])
    if not startup_result.ok:
        print(startup_result.error_message, file=sys.stderr)
        return 1

    window_host_controller = cast(WindowHostController, startup_context["window_host_controller"])
    main_manifest = cast(AppManifest, startup_context["main_manifest"])
    main_handle = startup_context["main_handle"]
    app.aboutToQuit.connect(runtime.begin_shutdown)
    emit_boot_ready(event_bus, main_window_id=main_manifest.id)
    action_result = register_runtime_window_actions(
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
        build_window_capability_properties=build_window_capability_properties,
    )
    if not action_result.ok:
        print(action_result.error_message, file=sys.stderr)
        return 1
    app.setProperty("_windowHostController", window_host_controller)
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
