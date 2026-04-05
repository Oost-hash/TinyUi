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
from runtime.app.paths import AppPaths
from runtime.events import startup_events, get_events_result
from runtime.persistence import startup_persistence, get_persistence_result, PersistenceStartupResult
from runtime.connectors import startup_connectors, get_connectors_result, ConnectorsStartupResult
from runtime.plugins import startup_plugins, get_plugins_result, PluginsStartupResult
from runtime.windows import startup_window_runtime, get_window_runtime_result, WindowRuntimeStartupResult
from widget_api import startup_widget_api, get_widget_api_result, WidgetApiStartupResult
from runtime.ui import start_runtime_ui
from runtime.widgets import start_runtime_widgets
from runtime_schema import EventBus, EventType, BootInitData, BootReadyData, StartupStep, run_startup_pipeline

if sys.platform == "win32":
    from ui_api.windowing import win_window  # noqa: F401  # eager import for Windows QML singletons


def emit_boot_init(event_bus: EventBus) -> None:
    """Emit the boot init event that prepares runtime state."""
    event_bus.emit_typed(EventType.BOOT_INIT, BootInitData(
        config_dir="",  # Runtime detects these via persistence domain
        plugins_dir="",
        data_dir="",
    ))


def emit_boot_ready(event_bus: EventBus, *, main_window_id: str) -> None:
    """Emit the boot ready event once the main window is known."""
    event_bus.emit_typed(EventType.BOOT_READY, BootReadyData(main_window_id=main_window_id))


def main() -> int:
    # Qt setup (needed before any QML operations)
    app = create_application()
    engine = create_engine()
    
    # Theme and actions (pure UI, no persistence needed)
    theme = Theme("dark")
    actions = AppActions()
    
    # Startup context for passing data between startup steps
    startup_context: dict[str, object] = {}

    # =========================================================================
    # PHASE 1: Domain startups (infrastructure layer)
    # =========================================================================
    
    def _start_events():
        """Step 1: Start events domain (creates EventBus)."""
        result = startup_events()
        if result.ok:
            event_bus = get_events_result()
            startup_context["event_bus"] = event_bus
            # Note: BOOT_INIT is emitted after Runtime is created (in Phase 2)
        return result

    def _start_persistence():
        """Step 2: Start persistence domain."""
        event_bus = cast(EventBus, startup_context.get("event_bus"))
        result = startup_persistence(event_bus)
        if result.ok:
            persistence = get_persistence_result()
            startup_context["persistence"] = persistence
        return result

    def _start_connectors():
        """Step 3: Start connector domain."""
        event_bus = cast(EventBus, startup_context.get("event_bus"))
        result = startup_connectors(event_bus)
        if result.ok:
            startup_context["connectors_result"] = get_connectors_result()
        return result

    def _start_widget_api():
        """Step 4: Start widget_api domain."""
        event_bus = cast(EventBus, startup_context.get("event_bus"))
        result = startup_widget_api(event_bus)
        if result.ok:
            startup_context["widget_api_result"] = get_widget_api_result()
        return result

    def _start_plugins():
        """Step 5: Start plugins domain."""
        event_bus = cast(EventBus, startup_context.get("event_bus"))
        # Plugin discovery needs AppPaths for plugin directories
        paths = AppPaths.detect()
        result = startup_plugins(event_bus, paths)
        if result.ok:
            startup_context["plugins_result"] = get_plugins_result()
        return result

    def _start_window_runtime():
        """Step 6: Start window runtime domain."""
        event_bus = cast(EventBus, startup_context.get("event_bus"))
        result = startup_window_runtime(event_bus)
        if result.ok:
            startup_context["window_runtime_result"] = get_window_runtime_result()
        return result

    # Run domain startup pipeline
    domain_startup_result = run_startup_pipeline([
        StartupStep("events", _start_events),
        StartupStep("persistence", _start_persistence),
        StartupStep("connectors", _start_connectors),
        StartupStep("widget_api", _start_widget_api),
        StartupStep("plugins", _start_plugins),
        StartupStep("window_runtime", _start_window_runtime),
    ])
    
    if not domain_startup_result.ok:
        print(domain_startup_result.error_message, file=sys.stderr)
        return 1

    # Extract startup results with proper typing
    event_bus = get_events_result()
    persistence = get_persistence_result()
    connectors_data = cast(ConnectorsStartupResult | None, startup_context.get("connectors_result"))
    widget_api_data = cast(WidgetApiStartupResult | None, startup_context.get("widget_api_result"))
    plugins_data = cast(PluginsStartupResult | None, startup_context.get("plugins_result"))
    window_runtime_data = cast(WindowRuntimeStartupResult | None, startup_context.get("window_runtime_result"))
    
    if event_bus is None:
        print("Events startup failed", file=sys.stderr)
        return 1
    if persistence is None:
        print("Persistence startup failed", file=sys.stderr)
        return 1
    
    # Extract registries from startup results
    connector_registry = connectors_data.registry if connectors_data else None
    widget_registry = widget_api_data.registry if widget_api_data else None
    window_runtime = window_runtime_data.window_runtime if window_runtime_data else None
    
    # =========================================================================
    # PHASE 2: Create Runtime (core orchestration layer)
    # =========================================================================
    
    runtime = Runtime(
        event_bus=event_bus,
        settings=persistence.settings,
        widget_store=persistence.widget_store,
        config_manager=persistence.config_manager,
        connector_registry=connector_registry,
        widget_registry=widget_registry,
        plugin_discovery=plugins_data.discovery if plugins_data else None,
        plugin_lifecycle=plugins_data.lifecycle if plugins_data else None,
        window_runtime=window_runtime,
    )
    
    # Create shared capabilities BEFORE BOOT_INIT so they receive events
    shared_capabilities = create_shared_capabilities(event_bus, runtime)
    startup_context["shared_capabilities"] = shared_capabilities
    
    # Emit BOOT_INIT now that Runtime and capabilities are ready
    emit_boot_init(event_bus)

    # =========================================================================
    # PHASE 3: UI startups (presentation layer)
    # =========================================================================
    
    def _start_runtime_ui():
        """Step 7: Start runtime UI."""
        return start_runtime_ui(runtime)

    def _start_window_host():
        """Step 8: Start window host."""
        event_bus = cast(EventBus, startup_context.get("event_bus"))
        controller, result = start_window_host(event_bus)
        startup_context["window_host_controller"] = controller
        return result

    def _open_main_window():
        """Step 9: Open main window."""
        event_bus = cast(EventBus, startup_context.get("event_bus"))
        shared_caps = startup_context.get("shared_capabilities")
        runtime_capabilities = create_runtime_capabilities(runtime, event_bus)
        startup_context["runtime_capabilities"] = runtime_capabilities
        
        main_manifest, main_handle, result = open_main_runtime_window(
            app=app,
            engine=engine,
            actions=actions,
            theme=theme,
            runtime=runtime,
            shared_capabilities=shared_caps,
            runtime_capabilities=runtime_capabilities,
            build_window_capability_properties=build_window_capability_properties,
        )
        startup_context["main_manifest"] = main_manifest
        startup_context["main_handle"] = main_handle
        return result

    def _start_runtime_widgets():
        """Step 10: Start runtime widgets."""
        return start_runtime_widgets(runtime)

    def _start_widget_host():
        """Step 11: Start widget host."""
        event_bus = cast(EventBus, startup_context.get("event_bus"))
        widget_host, result = start_widget_host(app, event_bus, runtime)
        startup_context["widget_host"] = widget_host
        return result

    # Run UI startup pipeline
    ui_startup_result = run_startup_pipeline([
        StartupStep("runtime_ui", _start_runtime_ui),
        StartupStep("window_host", _start_window_host),
        StartupStep("main_window", _open_main_window),
        StartupStep("runtime_widgets", _start_runtime_widgets),
        StartupStep("widget_host", _start_widget_host),
    ])
    
    if not ui_startup_result.ok:
        print(ui_startup_result.error_message, file=sys.stderr)
        return 1

    # =========================================================================
    # PHASE 4: Final initialization
    # =========================================================================
    
    # Extract UI results
    window_host_controller = cast(WindowHostController, startup_context["window_host_controller"])
    main_manifest = cast(AppManifest, startup_context["main_manifest"])
    main_handle = startup_context["main_handle"]
    runtime_capabilities = startup_context.get("runtime_capabilities")

    # Connect shutdown
    app.aboutToQuit.connect(runtime.begin_shutdown)
    
    # Emit boot ready
    emit_boot_ready(event_bus, main_window_id=main_manifest.id)
    
    # Register window actions
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
