from __future__ import annotations

from pathlib import Path

import plugins

from pkg_runtime_host import is_packaged_plugin_dir, mount_packaged_plugin
from runtimeV2.manifest.capabilities.load import ManifestLoad
from runtimeV2.manifest.registry import ManifestRegistry
from runtimeV2.paths.contracts import RuntimePaths
from runtimeV2.plugins.activation import PluginActivationStore
from runtimeV2.plugins.discovery import discover_plugins
from runtimeV2.plugins.registry import PluginRegistry
from runtimeV2.connectors.service_registry import ConnectorServiceRegistry
from runtimeV2.persistence.backends import SQLiteDocumentBackend
from runtimeV2.persistence.registry import PersistenceRegistry
from runtimeV2.persistence.repository import PersistenceRepository
from runtimeV2.persistence.schemas.settings import SettingDecl
from runtimeV2.persistence.settings import SettingsStore
from runtimeV2.persistence.startup_shutdown.register_persistence import register_persistence_document_schemas
from scripts.build_plugin import build_plugin


def _write_source_plugin(root: Path, plugin_id: str) -> Path:
    plugin_dir = root / plugin_id
    plugin_dir.mkdir(parents=True)
    (plugin_dir / "__init__.py").write_text("", encoding="utf-8")
    (plugin_dir / "plugin.py").write_text(
        "\n".join(
            [
                "LAST_ENABLED = None",
                "",
                "def activate(ctx):",
                "    global LAST_ENABLED",
                "    LAST_ENABLED = ctx.settings.get('enabled')",
            ]
        ),
        encoding="utf-8",
    )
    (plugin_dir / "manifest.toml").write_text(
        "\n".join(
            [
                "[plugin]",
                f'id = "{plugin_id}"',
                'type = "plugin"',
                'version = "1.2.3"',
                'author = "Test"',
                'description = "Packaged example"',
                'icon = "assets/logo.png"',
                "",
                "[[window]]",
                'id = "example.dialog"',
                'title = "Example"',
                'surface = "qml/surface.qml"',
                "",
                "[[setting]]",
                'key = "enabled"',
                'label = "Enabled"',
                "default = true",
                'type = "bool"',
            ]
        ),
        encoding="utf-8",
    )
    (plugin_dir / "qml").mkdir()
    (plugin_dir / "qml" / "surface.qml").write_text("import QtQuick\nItem {}", encoding="utf-8")
    (plugin_dir / "assets").mkdir()
    (plugin_dir / "assets" / "logo.png").write_bytes(b"png")
    return plugin_dir


def _settings_store(tmp_path: Path, plugin_id: str) -> SettingsStore:
    backend = SQLiteDocumentBackend(tmp_path / "settings.db")
    registry = PersistenceRegistry()
    register_persistence_document_schemas(registry)
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


def test_mount_packaged_plugin_extracts_runtime_and_preserves_manifest_root(tmp_path: Path) -> None:
    monkeypatch_appdata = tmp_path / "appdata"
    monkeypatch_appdata.mkdir(parents=True, exist_ok=True)
    import os
    os.environ["APPDATA"] = str(monkeypatch_appdata)

    plugin_dir = _write_source_plugin(tmp_path / "src_plugins", "example_plugin")
    package_dir = build_plugin(plugin_dir, tmp_path / "dist_plugins", clean=True, create_zip=False)

    assert is_packaged_plugin_dir(package_dir) is True

    mounted = mount_packaged_plugin(package_dir)

    assert mounted.plugin_id == "example_plugin"
    assert mounted.manifest_path == package_dir / "_internal" / "manifest.toml"
    assert mounted.plugin_root.exists()
    assert mounted.import_root.exists()
    assert (mounted.plugin_root / "plugin.pyc").exists()
    assert (mounted.plugin_root / "qml" / "surface.qml").exists()
    assert (mounted.plugin_root / "assets" / "logo.png").exists()


def test_discover_plugins_loads_packaged_plugin_manifest_and_activation(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("APPDATA", str(tmp_path / "appdata"))
    plugin_id = "example_plugin"
    plugin_dir = _write_source_plugin(tmp_path / "src_plugins", plugin_id)
    package_dir = build_plugin(plugin_dir, tmp_path / "dist_plugins", clean=True, create_zip=False)

    manifest_registry = ManifestRegistry()
    manifest_load = ManifestLoad(manifest_registry)
    runtime_paths = RuntimePaths(
        app_root=tmp_path,
        host_dir=tmp_path / "host_plugins" / "tinyui",
        plugins_dir=package_dir.parent,
        source_root=tmp_path,
        frozen_root=None,
    )
    runtime_paths.host_dir.mkdir(parents=True, exist_ok=True)
    (runtime_paths.host_dir / "manifest.toml").write_text(
        "\n".join(
            [
                "[plugin]",
                'id = "tinyui"',
                'type = "host"',
                'version = "1.0.0"',
                'author = "Test"',
                'description = "Host"',
                "",
                "[[window]]",
                'id = "tinyui.main"',
                'title = "TinyUi"',
            ]
        ),
        encoding="utf-8",
    )

    registry = discover_plugins(runtime_paths, manifest_load)

    assert plugin_id in registry.plugin_ids()
    assert registry.skipped_packaged_plugins() == set()

    manifest = manifest_registry.manifest(plugin_id)
    assert manifest is not None
    assert manifest.ui is not None
    assert manifest.ui.windows[0].surface is not None
    assert manifest.ui.windows[0].surface.exists()

    plugin_root = registry.plugin_root(plugin_id)
    assert plugin_root is not None
    import_root = next(root for root in registry.import_roots() if (root / "plugins" / plugin_id).exists())
    monkeypatch.syspath_prepend(str(import_root))

    activation = PluginActivationStore(
        registry=registry,
        settings=_settings_store(tmp_path, plugin_id),
        connector_services=ConnectorServiceRegistry(),
    )
    activation.activate_plugin(plugin_id)

    import importlib
    module = importlib.import_module(f"plugins.{plugin_id}.plugin")
    assert module.LAST_ENABLED is False


def test_discover_plugins_extends_plugins_package_path_for_packaged_plugins(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("APPDATA", str(tmp_path / "appdata"))
    plugin_id = "example_plugin"
    plugin_dir = _write_source_plugin(tmp_path / "src_plugins", plugin_id)
    package_dir = build_plugin(plugin_dir, tmp_path / "dist_plugins", clean=True, create_zip=False)

    manifest_registry = ManifestRegistry()
    manifest_load = ManifestLoad(manifest_registry)
    runtime_paths = RuntimePaths(
        app_root=tmp_path,
        host_dir=tmp_path / "host_plugins" / "tinyui",
        plugins_dir=package_dir.parent,
        source_root=tmp_path,
        frozen_root=None,
    )
    runtime_paths.host_dir.mkdir(parents=True, exist_ok=True)
    (runtime_paths.host_dir / "manifest.toml").write_text(
        "\n".join(
            [
                "[plugin]",
                'id = "tinyui"',
                'type = "host"',
                'version = "1.0.0"',
                'author = "Test"',
                'description = "Host"',
                "",
                "[[window]]",
                'id = "tinyui.main"',
                'title = "TinyUi"',
            ]
        ),
        encoding="utf-8",
    )

    original_package_path = list(plugins.__path__)
    try:
        registry = discover_plugins(runtime_paths, manifest_load)
        import_root = next(root for root in registry.import_roots() if (root / "plugins" / plugin_id).exists())
        assert str(import_root / "plugins") in plugins.__path__
    finally:
        plugins.__path__[:] = original_package_path
