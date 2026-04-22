"""Tests for runtime V2 plugin activation and lifecycle."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast

from runtimeV2.plugins.capabilities.active_read import PluginActiveRead
from runtimeV2.plugins.capabilities.active_write import PluginActiveWrite
from runtimeV2.plugins.capabilities.icon import PluginIconCapability
from runtimeV2.plugins.capabilities.state_read import PluginStateRead
from runtimeV2.plugins.capabilities.state_write import PluginStateWrite
from runtimeV2.connectors.poller import ConnectorServicePoller
from runtimeV2.connectors.service_registry import ConnectorServiceRegistry
from runtimeV2.connectors.startup_shutdown.startup import ConnectorsStartupResult
from runtimeV2.events.capabilities.event_read import EventRead
from runtimeV2.events.contracts import EventBus, EventType
from runtimeV2.events.event_registry import EventRegistry
from runtimeV2.events.startup_shutdown.startup import EventsStartupResult
from runtimeV2.manifest.capabilities.manifest_read import ManifestRead
from runtimeV2.manifest.registry import ManifestRegistry
from runtimeV2.persistence.backends import SQLiteDocumentBackend
from runtimeV2.persistence.registry import PersistenceRegistry
from runtimeV2.persistence.repository import PersistenceRepository
from runtimeV2.persistence.manifest.settings import SettingDecl
from runtimeV2.persistence.startup_shutdown.register_documents import register_persistence_documents
from runtimeV2.persistence.stores.settings import SettingsStore
from runtimeV2.plugins.activation import PluginActivationStore
from runtimeV2.plugins.lifecycle import PluginLifecycleStore
from runtimeV2.plugins.registry import PluginRegistry
from runtimeV2.plugins.schemas.manifest import PluginManifest
from runtimeV2.plugins.schemas.lifecycle import PluginErrorData, PluginState
from runtimeV2.plugins.startup_shutdown.startup import _initial_active_plugin_id


def _write_plugin_module(tmp_path: Path, plugin_id: str, body: str) -> Path:
    importlib.invalidate_caches()
    sys.modules.pop(f"plugins.{plugin_id}.plugin", None)
    sys.modules.pop(f"plugins.{plugin_id}", None)
    sys.modules.pop("plugins", None)
    package_root = tmp_path / "plugins" / plugin_id
    package_root.mkdir(parents=True, exist_ok=True)
    (tmp_path / "plugins" / "__init__.py").write_text("", encoding="utf-8")
    (package_root / "__init__.py").write_text("", encoding="utf-8")
    (package_root / "plugin.py").write_text(body, encoding="utf-8")
    return package_root


def _settings_store(tmp_path: Path, plugin_id: str) -> SettingsStore:
    backend = SQLiteDocumentBackend(tmp_path / "settings.db")
    registry = PersistenceRegistry()
    register_persistence_documents(registry)
    store = SettingsStore(PersistenceRepository(registry, backend))
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
    return ConnectorsStartupResult(
        registry=registry,
        poller=poller,
        declarations={},
        capabilities=cast(Any, SimpleNamespace()),
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


def test_plugin_capabilities_delegate_to_lifecycle_store(tmp_path, monkeypatch) -> None:
    """Plugin read/write capabilities should stay thin wrappers around lifecycle."""

    plugin_id = "demo_plugin"
    plugin_root = _write_plugin_module(
        tmp_path,
        plugin_id,
        """
def activate(ctx):
    return None

def deactivate(ctx):
    return None
""".strip(),
    )
    monkeypatch.syspath_prepend(str(tmp_path))

    registry = PluginRegistry()
    registry.register_plugin(plugin_id=plugin_id, plugin_root=plugin_root, source="source")
    lifecycle = PluginLifecycleStore(
        registry=registry,
        manifest_read=_manifest_read(plugin_id, "plugin"),
        connectors=_connectors_result(EventBus()),
        events=_events_result(EventBus()),
        activation=PluginActivationStore(
            registry=registry,
            settings=_settings_store(tmp_path, plugin_id),
            connector_services=ConnectorServiceRegistry(),
        ),
    )

    active_read = PluginActiveRead(lifecycle)
    active_write = PluginActiveWrite(lifecycle)
    state_read = PluginStateRead(lifecycle)
    state_write = PluginStateWrite(lifecycle)

    assert active_read.get_active_plugin() is None
    assert active_write.set_active_plugin(plugin_id) is True
    assert active_read.get_active_plugin() == plugin_id
    assert state_read.get_plugin_state(plugin_id) == PluginState.ACTIVE
    assert state_write.disable_plugin(plugin_id) is True
    assert state_read.get_plugin_state(plugin_id) == PluginState.DISABLED

    sys.modules.pop(f"plugins.{plugin_id}.plugin", None)
    sys.modules.pop(f"plugins.{plugin_id}", None)
    sys.modules.pop("plugins", None)


def test_plugin_icon_capability_resolves_safe_file_urls(tmp_path) -> None:
    """Plugin icon capability should resolve in-root asset URLs and reject missing files."""

    plugin_root = tmp_path / "plugins" / "demo_plugin"
    plugin_root.mkdir(parents=True, exist_ok=True)
    icon_dir = plugin_root / "assets"
    icon_dir.mkdir()
    icon_path = icon_dir / "logo.png"
    icon_path.write_bytes(b"png")

    registry = PluginRegistry()
    registry.register_plugin(plugin_id="demo_plugin", plugin_root=plugin_root, source="source")

    manifest_registry = ManifestRegistry()
    manifest_registry.register_manifest(
        manifest=PluginManifest(
            plugin_id="demo_plugin",
            plugin_type="plugin",
            version="1.0.0",
            author="Test",
            description="Plugin with icon",
            icon="assets/logo.png",
            requires=[],
        ),
        manifest_path=plugin_root / "manifest.toml",
        resource_root=plugin_root,
        source="source",
    )
    manifest_registry.register_manifest(
        manifest=PluginManifest(
            plugin_id="missing_plugin",
            plugin_type="plugin",
            version="1.0.0",
            author="Test",
            description="Missing icon",
            icon="assets/missing.png",
            requires=[],
        ),
        manifest_path=tmp_path / "plugins" / "missing_plugin" / "manifest.toml",
        resource_root=tmp_path / "plugins" / "missing_plugin",
        source="source",
    )
    registry.register_plugin(
        plugin_id="missing_plugin",
        plugin_root=tmp_path / "plugins" / "missing_plugin",
        source="source",
    )

    capability = PluginIconCapability(registry, ManifestRead(manifest_registry))

    assert capability.get_icon_url("demo_plugin") == icon_path.as_uri()
    assert capability.get_icon_url("missing_plugin") == ""


def test_plugin_icon_capability_rejects_absolute_and_parent_escape_paths(tmp_path) -> None:
    """Plugin icon paths should stay relative to the plugin root."""

    plugin_root = tmp_path / "plugins" / "demo_plugin"
    plugin_root.mkdir(parents=True, exist_ok=True)
    safe_icon_dir = plugin_root / "assets"
    safe_icon_dir.mkdir()
    (safe_icon_dir / "logo.png").write_bytes(b"png")

    outside_icon = tmp_path / "outside.png"
    outside_icon.write_bytes(b"png")

    registry = PluginRegistry()
    registry.register_plugin(plugin_id="escape_plugin", plugin_root=plugin_root, source="source")
    registry.register_plugin(plugin_id="absolute_plugin", plugin_root=plugin_root, source="source")

    manifest_registry = ManifestRegistry()
    manifest_registry.register_manifest(
        manifest=PluginManifest(
            plugin_id="escape_plugin",
            plugin_type="plugin",
            version="1.0.0",
            author="Test",
            description="Parent escape icon",
            icon="../outside.png",
            requires=[],
        ),
        manifest_path=plugin_root / "manifest.toml",
        resource_root=plugin_root,
        source="source",
    )
    manifest_registry.register_manifest(
        manifest=PluginManifest(
            plugin_id="absolute_plugin",
            plugin_type="plugin",
            version="1.0.0",
            author="Test",
            description="Absolute icon",
            icon=str(outside_icon),
            requires=[],
        ),
        manifest_path=plugin_root / "manifest.toml",
        resource_root=plugin_root,
        source="source",
    )

    capability = PluginIconCapability(registry, ManifestRead(manifest_registry))

    assert capability.get_icon_url("escape_plugin") == ""
    assert capability.get_icon_url("absolute_plugin") == ""


def test_initial_active_plugin_picks_first_enabled_plugin_or_overlay() -> None:
    """Boot policy should pick the first enabled plugin or overlay from manifest order."""

    registry = ManifestRegistry()
    registry.register_manifest(
        manifest=PluginManifest(
            plugin_id="tinyui",
            plugin_type="host",
            version="1.0.0",
            author="Test",
            description="Host",
            icon="",
            requires=[],
        ),
        manifest_path=Path("tinyui/manifest.toml"),
        resource_root=Path("tinyui"),
        source="host",
    )
    registry.register_manifest(
        manifest=PluginManifest(
            plugin_id="demo_overlay",
            plugin_type="overlay",
            version="1.0.0",
            author="Test",
            description="Overlay",
            icon="",
            requires=[],
        ),
        manifest_path=Path("demo_overlay/manifest.toml"),
        resource_root=Path("demo_overlay"),
        source="source",
    )
    registry.register_manifest(
        manifest=PluginManifest(
            plugin_id="dummy_plugin",
            plugin_type="plugin",
            version="1.0.0",
            author="Test",
            description="Plugin",
            icon="",
            requires=[],
        ),
        manifest_path=Path("dummy_plugin/manifest.toml"),
        resource_root=Path("dummy_plugin"),
        source="source",
    )

    settings = SimpleNamespace(
        get=lambda namespace, key: {
            ("demo_overlay", "enabled"): True,
            ("dummy_plugin", "enabled"): True,
        }.get((namespace, key)),
    )
    persistence = cast(Any, SimpleNamespace(settings=settings))

    assert _initial_active_plugin_id(
        manifest_read=ManifestRead(registry),
        persistence=persistence,
    ) == "demo_overlay"

