"""Tests for runtime V2 plugin activation and lifecycle."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path
from typing import cast

from runtimeV2.connectors.poller import ConnectorServicePoller
from runtimeV2.connectors.register_capabilities import register_connector_capabilities
from runtimeV2.connectors.service_registry import ConnectorServiceRegistry
from runtimeV2.connectors.startup import ConnectorsStartupResult
from runtimeV2.events.capabilities.event_read import EventRead
from runtimeV2.events.contracts import EventBus, EventType
from runtimeV2.events.event_registry import EventRegistry
from runtimeV2.events.startup import EventsStartupResult
from runtimeV2.manifest.capabilities.manifest_read import ManifestRead
from runtimeV2.manifest.registry import ManifestRegistry
from runtimeV2.persistence.contracts import PersistencePaths
from runtimeV2.persistence.schemas.settings import SettingDecl
from runtimeV2.persistence.settings import SettingsStore
from runtimeV2.plugins.activation import PluginActivationStore
from runtimeV2.plugins.lifecycle import PluginLifecycleStore
from runtimeV2.plugins.registry import PluginRegistry
from runtimeV2.plugins.schemas.manifest import PluginManifest
from runtimeV2.plugins.schemas.lifecycle import PluginErrorData, PluginState


def _write_plugin_module(tmp_path: Path, plugin_id: str, body: str) -> Path:
    package_root = tmp_path / "plugins" / plugin_id
    package_root.mkdir(parents=True, exist_ok=True)
    (tmp_path / "plugins" / "__init__.py").write_text("", encoding="utf-8")
    (package_root / "__init__.py").write_text("", encoding="utf-8")
    (package_root / "plugin.py").write_text(body, encoding="utf-8")
    return package_root


def _settings_store(tmp_path: Path, plugin_id: str) -> SettingsStore:
    base_dir = tmp_path / "TinyUi"
    config_root = base_dir / "config"
    paths = PersistencePaths(
        base_dir=base_dir,
        config_root=config_root,
        cache_dir=base_dir / "cache",
        logs_dir=base_dir / "logs",
        bootstrap_path=base_dir / "bootstrap.toml",
        config_sets_path=config_root / "config_sets.json",
    )
    store = SettingsStore(paths, "default")
    store.register_specs(
        {
            plugin_id: [
                SettingDecl(key="enabled", label="Enabled", type="bool", default=True),
            ]
        }
    )
    store.set(plugin_id, "enabled", False)
    return store


def _manifest_read(plugin_id: str, plugin_type: str) -> ManifestRead:
    registry = ManifestRegistry()
    registry.register_manifest(
        manifest=PluginManifest(
            plugin_id=plugin_id,
            plugin_type=plugin_type,
            version="1.0.0",
            author="Test",
            description="Test plugin",
            icon="",
            requires=[],
        ),
        manifest_path=Path(f"{plugin_id}/manifest.toml"),
        resource_root=Path(plugin_id),
        source="source",
    )
    return ManifestRead(registry)


def _connectors_result(bus: EventBus) -> ConnectorsStartupResult:
    registry = ConnectorServiceRegistry()
    poller = ConnectorServicePoller(registry, bus)
    capabilities = register_connector_capabilities(registry, poller)
    return ConnectorsStartupResult(
        registry=registry,
        poller=poller,
        declarations={},
        capabilities=capabilities,
    )


def _events_result(bus: EventBus) -> EventsStartupResult:
    registry = EventRegistry()
    return EventsStartupResult(
        bus=bus,
        registry=registry,
        event_read=EventRead(registry),
    )


def test_plugin_activation_store_imports_module_and_passes_scoped_settings(tmp_path, monkeypatch) -> None:
    """Activation should import plugin.py and expose scoped settings."""

    plugin_id = "test_plugin"
    plugin_root = _write_plugin_module(
        tmp_path,
        plugin_id,
        """
LAST_ENABLED = None
DEACTIVATED = False

def activate(ctx):
    global LAST_ENABLED
    LAST_ENABLED = ctx.settings.get("enabled")

def deactivate(ctx):
    global DEACTIVATED
    DEACTIVATED = True
""".strip(),
    )
    monkeypatch.syspath_prepend(str(tmp_path))

    registry = PluginRegistry()
    registry.register_plugin(plugin_id=plugin_id, plugin_root=plugin_root, source="source")
    settings = _settings_store(tmp_path, plugin_id)
    activation = PluginActivationStore(
        registry=registry,
        settings=settings,
        connector_services=ConnectorServiceRegistry(),
    )

    activation.activate_plugin(plugin_id)
    activation.deactivate_plugin(plugin_id)

    module = importlib.import_module(f"plugins.{plugin_id}.plugin")
    assert module.LAST_ENABLED is False
    assert module.DEACTIVATED is True
    sys.modules.pop(f"plugins.{plugin_id}.plugin", None)
    sys.modules.pop(f"plugins.{plugin_id}", None)
    sys.modules.pop("plugins", None)


def test_plugin_lifecycle_activates_plugin_and_emits_error(tmp_path, monkeypatch) -> None:
    """Lifecycle should use activation and expose plugin errors via events."""

    plugin_id = "broken_plugin"
    plugin_root = _write_plugin_module(
        tmp_path,
        plugin_id,
        """
def activate(ctx):
    raise RuntimeError("boom")
""".strip(),
    )
    monkeypatch.syspath_prepend(str(tmp_path))

    registry = PluginRegistry()
    registry.register_plugin(plugin_id=plugin_id, plugin_root=plugin_root, source="source")
    settings = _settings_store(tmp_path, plugin_id)
    bus = EventBus()
    lifecycle = PluginLifecycleStore(
        registry=registry,
        manifest_read=_manifest_read(plugin_id, "plugin"),
        connectors=_connectors_result(bus),
        events=_events_result(bus),
        activation=PluginActivationStore(
            registry=registry,
            settings=settings,
            connector_services=ConnectorServiceRegistry(),
        ),
    )

    assert lifecycle.enable_plugin(plugin_id) is False
    assert lifecycle.get_plugin_state(plugin_id) == PluginState.ERROR
    assert [event.type for event in bus.get_history()] == [
        EventType.PLUGIN_STATE_CHANGED,
        EventType.PLUGIN_STATE_CHANGED,
        EventType.PLUGIN_STATE_CHANGED,
        EventType.PLUGIN_ERROR,
    ]
    error_event = bus.get_history(EventType.PLUGIN_ERROR)[-1]
    assert cast(PluginErrorData, error_event.data).error_message == "boom"
    sys.modules.pop(f"plugins.{plugin_id}.plugin", None)
    sys.modules.pop(f"plugins.{plugin_id}", None)
    sys.modules.pop("plugins", None)
