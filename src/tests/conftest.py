"""Pytest configuration for TinyUI tests."""

import sys
from pathlib import Path
from typing import Generator

import pytest

# Add src to Python path for all tests
src_path = str(Path(__file__).parent.parent)
if src_path not in sys.path:
    sys.path.insert(0, src_path)


@pytest.fixture
def booted_runtime() -> Generator:
    """Create a fully booted Runtime with all dependencies.
    
    This fixture uses the startup functions to create a properly
    initialized Runtime with all required dependencies.
    """
    from runtime.events import startup_events, get_events_result
    from runtime.persistence import startup_persistence, get_persistence_result
    from runtime.connectors import startup_connectors, get_connectors_result
    from runtime.plugins import startup_plugins, get_plugins_result
    from runtime.windows import startup_window_runtime, get_window_runtime_result
    from widget_api import startup_widget_api, get_widget_api_result
    from runtime.app.paths import AppPaths
    from runtime.runtime import Runtime
    from runtime_schema import run_startup_pipeline, StartupStep

    # Phase 1: Start all domains
    domain_result = run_startup_pipeline([
        StartupStep("events", startup_events),
        StartupStep("persistence", lambda: startup_persistence(get_events_result())),
        StartupStep("connectors", lambda: startup_connectors(get_events_result())),
        StartupStep("widget_api", lambda: startup_widget_api(get_events_result())),
        StartupStep("plugins", lambda: startup_plugins(get_events_result(), AppPaths.detect())),
        StartupStep("window_runtime", lambda: startup_window_runtime(get_events_result())),
    ])

    if not domain_result.ok:
        pytest.skip(f"Domain startup failed: {domain_result.error_message}")

    # Get all startup results
    event_bus = get_events_result()
    persistence = get_persistence_result()
    connectors_data = get_connectors_result()
    widget_api_data = get_widget_api_result()
    plugins_data = get_plugins_result()
    window_runtime_data = get_window_runtime_result()

    if event_bus is None or persistence is None:
        pytest.skip("Required startup results not available")

    # Create Runtime with all dependencies
    runtime = Runtime(
        event_bus=event_bus,
        settings=persistence.settings,
        widget_store=persistence.widget_store,
        config_manager=persistence.config_manager,
        connector_registry=connectors_data.registry if connectors_data else None,
        widget_registry=widget_api_data.registry if widget_api_data else None,
        plugin_discovery=plugins_data.discovery if plugins_data else None,
        plugin_lifecycle=plugins_data.lifecycle if plugins_data else None,
        window_runtime=window_runtime_data.window_runtime if window_runtime_data else None,
    )

    # Emit boot init to complete runtime initialization
    from runtime_schema import EventType, BootInitData
    event_bus.emit_typed(EventType.BOOT_INIT, BootInitData(config_dir="", plugins_dir="", data_dir=""))

    yield runtime


def create_test_runtime_with_paths(paths) -> "Runtime":
    """Create a Runtime with custom AppPaths for testing.
    
    This is useful for tests that need to set up custom plugin directories
    and still want a properly initialized Runtime.
    """
    from runtime.events import startup_events, get_events_result
    from runtime.persistence import (
        startup_persistence, get_persistence_result,
        ConfigResolver, SettingsRegistry, WidgetConfigStore, ConfigSetManager,
    )
    from runtime.connectors import startup_connectors, get_connectors_result
    from runtime.windows import startup_window_runtime, get_window_runtime_result
    from widget_api import startup_widget_api, get_widget_api_result
    from runtime.runtime import Runtime
    from runtime_schema import run_startup_pipeline, StartupStep

    # Start event bus first
    events_result = startup_events()
    if not events_result.ok:
        raise RuntimeError("Failed to start events")
    event_bus = get_events_result()
    if event_bus is None:
        raise RuntimeError("Event bus not available")

    # Create persistence with a fresh resolver pointing to the test paths
    resolver = ConfigResolver()
    # Override the config directory to use the test paths
    resolver._base_config_dir = paths.config_dir  # type: ignore
    resolver._base_config_dir.mkdir(parents=True, exist_ok=True)
    
    config_manager = ConfigSetManager(resolver)
    active_set = config_manager.get_active()
    settings = SettingsRegistry(resolver, active_set.id)
    widget_store = WidgetConfigStore(resolver, active_set.id)

    # Start other domains
    startup_connectors(event_bus)
    startup_widget_api(event_bus)
    startup_window_runtime(event_bus)

    connectors_data = get_connectors_result()
    widget_api_data = get_widget_api_result()
    window_runtime_data = get_window_runtime_result()

    # Create Runtime
    runtime = Runtime(
        event_bus=event_bus,
        settings=settings,
        widget_store=widget_store,
        config_manager=config_manager,
        connector_registry=connectors_data.registry if connectors_data else None,
        widget_registry=widget_api_data.registry if widget_api_data else None,
        window_runtime=window_runtime_data.window_runtime if window_runtime_data else None,
    )
    
    # Manually set paths since we bypassed normal boot
    runtime.paths = paths
    
    return runtime


def create_minimal_test_runtime(bus=None):
    """Create a minimal Runtime for tests that don't need full persistence.
    
    This creates a Runtime with minimal required dependencies for tests
    that just need to test window runtime behavior in isolation.
    """
    from runtime.events import get_events_result
    from runtime.persistence import (
        ConfigResolver, SettingsRegistry, WidgetConfigStore, ConfigSetManager,
    )
    from runtime.connectors import startup_connectors, get_connectors_result
    from runtime.windows import startup_window_runtime, get_window_runtime_result
    from widget_api import startup_widget_api, get_widget_api_result
    from runtime.runtime import Runtime
    
    if bus is None:
        from runtime.events import startup_events
        result = startup_events()
        if not result.ok:
            raise RuntimeError("Failed to start events")
        bus = get_events_result()
        if bus is None:
            raise RuntimeError("Event bus not available")
    
    # Create minimal persistence
    resolver = ConfigResolver()
    resolver._base_dir.mkdir(parents=True, exist_ok=True)
    
    config_manager = ConfigSetManager(resolver)
    active_set = config_manager.get_active()
    settings = SettingsRegistry(resolver, active_set.id)
    widget_store = WidgetConfigStore(resolver, active_set.id)
    
    # Start other domains
    startup_connectors(bus)
    startup_widget_api(bus)
    startup_window_runtime(bus)
    
    connectors_data = get_connectors_result()
    widget_api_data = get_widget_api_result()
    window_runtime_data = get_window_runtime_result()
    
    return Runtime(
        event_bus=bus,
        settings=settings,
        widget_store=widget_store,
        config_manager=config_manager,
        connector_registry=connectors_data.registry if connectors_data else None,
        widget_registry=widget_api_data.registry if widget_api_data else None,
        window_runtime=window_runtime_data.window_runtime if window_runtime_data else None,
    )
