"""Tests for manifest-driven plugins without plugin.py lifecycle modules."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from capabilities.plugin_read import PluginRead
from runtime.app.paths import AppPaths
from runtime.manifest import load_plugin_manifest
from runtime.persistence import SettingsRegistry
from runtime.runtime import Runtime
from runtime_schema import EventBus, EventType


def _write_manifest(
    plugin_dir: Path,
    plugin_id: str,
    plugin_type: str,
    *,
    icon: str | None = None,
    requires: list[str] | None = None,
    connector_provides: list[str] | None = None,
    provider_module: str | None = None,
    provider_class: str | None = None,
) -> None:
    plugin_dir.mkdir(parents=True, exist_ok=True)
    (plugin_dir / "__init__.py").write_text("", encoding="utf-8")
    lines = [
        "[plugin]",
        f'id = "{plugin_id}"',
        f'type = "{plugin_type}"',
        'version = "1.0.0"',
        'author = "Test"',
        f'description = "{plugin_id}"',
    ]
    if icon is not None:
        lines.append(f'icon = "{icon}"')
    if requires:
        rendered = ", ".join(f'"{item}"' for item in requires)
        lines.append(f"requires = [{rendered}]")
    lines.append("")
    if plugin_type == "host":
        lines.extend(
            [
                "[[window]]",
                f'id = "{plugin_id}.main"',
                f'title = "{plugin_id}"',
                'surface = "app_main/qml/surface.qml"',
                "",
            ]
        )
    if connector_provides:
        rendered = ", ".join(f'"{item}"' for item in connector_provides)
        lines.extend(
            [
                "[connector]",
                f"provides = [{rendered}]",
                "",
            ]
        )
    if provider_module and provider_class:
        lines.extend(
            [
                "[provider]",
                f'module = "{provider_module}"',
                f'class = "{provider_class}"',
                "",
            ]
        )
    (plugin_dir / "manifest.toml").write_text("\n".join(lines), encoding="utf-8")


def _clear_test_modules() -> None:
    for name in [
        "plugins.dumb_plugin.plugin",
        "plugins.dumb_plugin",
        "plugins.dummy_plugin.plugin",
        "plugins.dummy_plugin",
        "plugins.tinyui.plugin",
        "plugins.tinyui",
        "plugins",
        "plugins.a_plain_plugin",
        "plugins.a_plain_plugin.plugin",
        "plugins.b_consumer_plugin",
        "plugins.b_consumer_plugin.plugin",
        "plugins.telemetry_connector",
        "plugins.telemetry_connector.plugin",
    ]:
        sys.modules.pop(name, None)
    importlib.invalidate_caches()


@pytest.fixture
def manifest_plugin_runtime(tmp_path: Path):
    """Create a runtime with one manifest-only plugin and one Python-backed plugin."""
    _clear_test_modules()

    source_root = tmp_path / "src"
    plugins_dir = source_root / "plugins"
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"

    plugins_dir.mkdir(parents=True, exist_ok=True)
    (plugins_dir / "__init__.py").write_text("", encoding="utf-8")

    _write_manifest(plugins_dir / "tinyui", "tinyui", "host")
    (plugins_dir / "tinyui" / "plugin.py").write_text(
        "def activate(ctx):\n    return None\n",
        encoding="utf-8",
    )

    _write_manifest(plugins_dir / "dumb_plugin", "dumb_plugin", "plugin")

    _write_manifest(plugins_dir / "dummy_plugin", "dummy_plugin", "plugin")
    (plugins_dir / "dummy_plugin" / "plugin.py").write_text(
        "\n".join(
            [
                "ACTIVATE_CALLS = 0",
                "DEACTIVATE_CALLS = 0",
                "",
                "def activate(ctx):",
                "    global ACTIVATE_CALLS",
                "    ACTIVATE_CALLS += 1",
                "",
                "def deactivate(ctx):",
                "    global DEACTIVATE_CALLS",
                "    DEACTIVATE_CALLS += 1",
                "",
            ]
        ),
        encoding="utf-8",
    )

    paths = AppPaths(
        app_root=source_root,
        config_dir=config_dir,
        host_dir=plugins_dir / "tinyui",
        plugins_dir=plugins_dir,
        data_dir=data_dir,
        source_root=source_root,
        frozen_root=None,
    )
    config_dir.mkdir(parents=True, exist_ok=True)
    data_dir.mkdir(parents=True, exist_ok=True)

    bus = EventBus()
    runtime = Runtime(bus)
    runtime.paths = paths
    runtime.settings = SettingsRegistry(config_dir)

    try:
        runtime._do_boot()
        yield runtime, bus
    finally:
        plugins_parent = str(plugins_dir.parent)
        if plugins_parent in sys.path:
            sys.path.remove(plugins_parent)
        _clear_test_modules()


def test_manifest_only_plugin_can_be_reactivated_after_switch(manifest_plugin_runtime) -> None:
    """Manifest-only plugins stay switchable without a plugin.py lifecycle module."""
    runtime, bus = manifest_plugin_runtime

    activated_plugins: list[str] = []
    bus.on(EventType.PLUGIN_ACTIVATED, lambda e: activated_plugins.append(e.data.plugin_id))

    assert runtime.active_plugin == "dumb_plugin"
    assert runtime.get_plugin_state("dumb_plugin").name.lower() == "active"

    assert runtime.set_active_plugin("dummy_plugin") is True
    assert runtime.active_plugin == "dummy_plugin"
    assert runtime.get_plugin_state("dummy_plugin").name.lower() == "active"

    assert runtime.set_active_plugin("dumb_plugin") is True
    assert runtime.active_plugin == "dumb_plugin"
    assert runtime.get_plugin_state("dumb_plugin").name.lower() == "active"
    assert runtime.get_plugin_state("dumb_plugin").name.lower() != "error"

    assert activated_plugins == ["dummy_plugin", "dumb_plugin"]

    dummy_module = importlib.import_module("plugins.dummy_plugin.plugin")
    assert dummy_module.DEACTIVATE_CALLS == 1


@pytest.fixture
def provider_runtime(tmp_path: Path):
    """Create a runtime with a connector-backed provider and two plugins."""
    _clear_test_modules()

    source_root = tmp_path / "src"
    plugins_dir = source_root / "plugins"
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"

    plugins_dir.mkdir(parents=True, exist_ok=True)
    (plugins_dir / "__init__.py").write_text("", encoding="utf-8")

    _write_manifest(plugins_dir / "tinyui", "tinyui", "host")
    (plugins_dir / "tinyui" / "plugin.py").write_text("def activate(ctx):\n    return None\n", encoding="utf-8")

    _write_manifest(plugins_dir / "a_plain_plugin", "a_plain_plugin", "plugin")
    _write_manifest(
        plugins_dir / "b_consumer_plugin",
        "b_consumer_plugin",
        "plugin",
        requires=["telemetry_connector"],
    )
    (plugins_dir / "b_consumer_plugin" / "plugin.py").write_text(
        "def activate(ctx):\n    return None\n",
        encoding="utf-8",
    )

    _write_manifest(
        plugins_dir / "telemetry_connector",
        "telemetry_connector",
        "connector",
        connector_provides=["telemetry.tyre.v1"],
        provider_module="plugins.telemetry_connector.plugin",
        provider_class="TelemetryConnector",
    )
    (plugins_dir / "telemetry_connector" / "plugin.py").write_text(
        "\n".join(
            [
                "class TelemetryConnector:",
                "    def __init__(self):",
                "        self._opened = False",
                "        self._active_source = 'none'",
                "        self._requests = {}",
                "",
                "    def supports_source(self, name):",
                "        return name in ('mock', 'live')",
                "",
                "    def request_source(self, owner, source_name):",
                "        self._requests[owner] = source_name",
                "        self._active_source = source_name",
                "        return True",
                "",
                "    def release_source(self, owner):",
                "        self._requests.pop(owner, None)",
                "        self._active_source = next(reversed(self._requests.values())) if self._requests else 'none'",
                "        return True",
                "",
                "    def open(self):",
                "        self._opened = True",
                "",
                "    def close(self):",
                "        self._opened = False",
                "",
                "    def update(self):",
                "        return None",
                "",
                "    def inspect_snapshot(self):",
                "        return [",
                "            ('provider.mode', 'demo' if self._opened else 'inactive'),",
                "            ('provider.active_source', self._active_source),",
                "            ('tyre.compound_f', 'Soft'),",
                "            ('tyre.compound_r', 'Soft'),",
                "        ]",
                "",
                "def activate(ctx):",
                "    return None",
                "",
                "def deactivate(ctx):",
                "    return None",
                "",
            ]
        ),
        encoding="utf-8",
    )

    paths = AppPaths(
        app_root=source_root,
        config_dir=config_dir,
        host_dir=plugins_dir / "tinyui",
        plugins_dir=plugins_dir,
        data_dir=data_dir,
        source_root=source_root,
        frozen_root=None,
    )
    config_dir.mkdir(parents=True, exist_ok=True)
    data_dir.mkdir(parents=True, exist_ok=True)

    bus = EventBus()
    runtime = Runtime(bus)
    runtime.paths = paths
    runtime.settings = SettingsRegistry(config_dir)

    try:
        runtime._do_boot()
        yield runtime, bus
    finally:
        plugins_parent = str(plugins_dir.parent)
        if plugins_parent in sys.path:
            sys.path.remove(plugins_parent)
        _clear_test_modules()


def test_connector_provider_tracks_active_plugin_dependencies(provider_runtime) -> None:
    """Providers register only while their connector is required by the active plugin."""
    runtime, bus = provider_runtime

    registered: list[str] = []
    unregistered: list[str] = []
    bus.on(EventType.PROVIDER_REGISTERED, lambda e: registered.append(e.data.provider_id))
    bus.on(EventType.PROVIDER_UNREGISTERED, lambda e: unregistered.append(e.data.provider_id))

    assert runtime.active_plugin == "a_plain_plugin"
    assert runtime.get_plugin_state("telemetry_connector").name.lower() == "disabled"
    assert runtime.providers.has("telemetry_connector") is False

    assert runtime.set_active_plugin("b_consumer_plugin") is True
    assert runtime.get_plugin_state("telemetry_connector").name.lower() == "active"
    assert runtime.providers.has("telemetry_connector") is True
    assert runtime.providers.inspect("telemetry_connector")[0][1] == "demo"

    assert runtime.set_active_plugin("a_plain_plugin") is True
    assert runtime.get_plugin_state("telemetry_connector").name.lower() == "disabled"
    assert runtime.providers.has("telemetry_connector") is False
    assert registered == ["telemetry_connector"]
    assert unregistered == ["telemetry_connector"]


def test_manifest_parses_plugin_icon_field(tmp_path: Path) -> None:
    """Plugin manifests expose icon declarations from the [plugin] block."""
    plugin_dir = tmp_path / "example_plugin"
    _write_manifest(plugin_dir, "example_plugin", "plugin", icon="assets/logo.png")

    manifest = load_plugin_manifest(plugin_dir / "manifest.toml")

    assert manifest.icon == "assets/logo.png"


def test_runtime_projects_plugin_icon_url_for_valid_plugin_asset(tmp_path: Path) -> None:
    """PluginRead exposes resolved plugin-owned icon URLs."""
    _clear_test_modules()

    source_root = tmp_path / "src"
    plugins_dir = source_root / "plugins"
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"

    plugins_dir.mkdir(parents=True, exist_ok=True)
    (plugins_dir / "__init__.py").write_text("", encoding="utf-8")

    _write_manifest(plugins_dir / "tinyui", "tinyui", "host")
    (plugins_dir / "tinyui" / "plugin.py").write_text("def activate(ctx):\n    return None\n", encoding="utf-8")

    _write_manifest(plugins_dir / "dummy_plugin", "dummy_plugin", "plugin", icon="assets/logo.png")
    (plugins_dir / "dummy_plugin" / "assets").mkdir(parents=True, exist_ok=True)
    (plugins_dir / "dummy_plugin" / "assets" / "logo.png").write_bytes(b"png")

    paths = AppPaths(
        app_root=source_root,
        config_dir=config_dir,
        host_dir=plugins_dir / "tinyui",
        plugins_dir=plugins_dir,
        data_dir=data_dir,
        source_root=source_root,
        frozen_root=None,
    )
    config_dir.mkdir(parents=True, exist_ok=True)
    data_dir.mkdir(parents=True, exist_ok=True)

    runtime = Runtime(EventBus())
    runtime.paths = paths
    runtime.settings = SettingsRegistry(config_dir)

    try:
        runtime._do_boot()

        plugin_read = PluginRead(runtime)
        plugin_entry = next(plugin for plugin in plugin_read.items() if plugin["id"] == "dummy_plugin")

        assert plugin_entry["iconUrl"].endswith("/plugins/dummy_plugin/assets/logo.png")
        assert plugin_entry["iconUrl"].startswith("file:///")
    finally:
        plugins_parent = str(plugins_dir.parent)
        if plugins_parent in sys.path:
            sys.path.remove(plugins_parent)
        _clear_test_modules()


def test_runtime_rejects_plugin_icon_outside_plugin_root(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Runtime ignores icon declarations that escape the plugin boundary."""
    _clear_test_modules()

    source_root = tmp_path / "src"
    plugins_dir = source_root / "plugins"
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"

    plugins_dir.mkdir(parents=True, exist_ok=True)
    (plugins_dir / "__init__.py").write_text("", encoding="utf-8")

    _write_manifest(plugins_dir / "tinyui", "tinyui", "host")
    (plugins_dir / "tinyui" / "plugin.py").write_text("def activate(ctx):\n    return None\n", encoding="utf-8")

    _write_manifest(plugins_dir / "dummy_plugin", "dummy_plugin", "plugin", icon="../outside/logo.png")

    paths = AppPaths(
        app_root=source_root,
        config_dir=config_dir,
        host_dir=plugins_dir / "tinyui",
        plugins_dir=plugins_dir,
        data_dir=data_dir,
        source_root=source_root,
        frozen_root=None,
    )
    config_dir.mkdir(parents=True, exist_ok=True)
    data_dir.mkdir(parents=True, exist_ok=True)

    runtime = Runtime(EventBus())
    runtime.paths = paths
    runtime.settings = SettingsRegistry(config_dir)

    try:
        runtime._do_boot()
        plugin_read = PluginRead(runtime)
        plugin_entry = next(plugin for plugin in plugin_read.items() if plugin["id"] == "dummy_plugin")
        captured = capsys.readouterr()

        assert plugin_entry["iconUrl"] == ""
        assert "Ignoring invalid plugin icon" in captured.err
        assert "resolved outside plugin root" in captured.err
    finally:
        plugins_parent = str(plugins_dir.parent)
        if plugins_parent in sys.path:
            sys.path.remove(plugins_parent)
        _clear_test_modules()


def test_runtime_rejects_missing_plugin_icon_file(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Runtime ignores icon declarations whose files do not exist."""
    _clear_test_modules()

    source_root = tmp_path / "src"
    plugins_dir = source_root / "plugins"
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"

    plugins_dir.mkdir(parents=True, exist_ok=True)
    (plugins_dir / "__init__.py").write_text("", encoding="utf-8")

    _write_manifest(plugins_dir / "tinyui", "tinyui", "host")
    (plugins_dir / "tinyui" / "plugin.py").write_text("def activate(ctx):\n    return None\n", encoding="utf-8")

    _write_manifest(plugins_dir / "dummy_plugin", "dummy_plugin", "plugin", icon="assets/missing.png")

    paths = AppPaths(
        app_root=source_root,
        config_dir=config_dir,
        host_dir=plugins_dir / "tinyui",
        plugins_dir=plugins_dir,
        data_dir=data_dir,
        source_root=source_root,
        frozen_root=None,
    )
    config_dir.mkdir(parents=True, exist_ok=True)
    data_dir.mkdir(parents=True, exist_ok=True)

    runtime = Runtime(EventBus())
    runtime.paths = paths
    runtime.settings = SettingsRegistry(config_dir)

    try:
        runtime._do_boot()
        plugin_read = PluginRead(runtime)
        plugin_entry = next(plugin for plugin in plugin_read.items() if plugin["id"] == "dummy_plugin")
        captured = capsys.readouterr()

        assert plugin_entry["iconUrl"] == ""
        assert "Ignoring invalid plugin icon" in captured.err
        assert "file not found" in captured.err
    finally:
        plugins_parent = str(plugins_dir.parent)
        if plugins_parent in sys.path:
            sys.path.remove(plugins_parent)
        _clear_test_modules()
