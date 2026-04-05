from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest

from runtime.app.paths import AppPaths
from runtime.connectors import register_connector_service
from runtime.manifest import load_plugin_manifest
from runtime.persistence import SettingsRegistry
from runtime.runtime import Runtime
from runtime_schema import EventBus
from runtime.widgets import WidgetRuntimeStatus, detect_active_game_id
from widget_api import create_default_widget_registry


def _clear_widget_api_test_modules() -> None:
    for name in list(sys.modules):
        if name == "plugins" or name.startswith("plugins."):
            sys.modules.pop(name, None)
    importlib.invalidate_caches()


def test_default_widget_registry_contains_expected_widget_requirements() -> None:
    registry = create_default_widget_registry()

    assert registry.has("textWidget") is True
    definition = registry.get("textWidget")
    assert definition is not None
    assert definition.required_bindings == ("source",)
    assert registry.get("missing.kind") is None


def test_manifest_parses_widget_declarations_for_overlay(tmp_path: Path) -> None:
    plugin_dir = tmp_path / "demo_overlay"
    plugin_dir.mkdir(parents=True)
    (plugin_dir / "manifest.toml").write_text(
        "\n".join(
            [
                "[plugin]",
                'id = "demo_overlay"',
                'type = "overlay"',
                'version = "1.0.0"',
                'author = "Test"',
                'description = "overlay"',
                "",
                "[[widget]]",
                'id = "session_time_left"',
                'widget = "textWidget"',
                'label = "Time Left"',
                'bindings = { source = "session.time_left" }',
                "",
            ]
        ),
        encoding="utf-8",
    )

    manifest = load_plugin_manifest(plugin_dir / "manifest.toml")

    assert manifest.plugin_type == "overlay"
    assert manifest.overlay is not None
    assert manifest.overlay.connectors == []
    assert [widget.id for widget in manifest.overlay.widgets] == ["session_time_left"]
    assert manifest.overlay.widgets[0].widget == "textWidget"
    assert manifest.overlay.widgets[0].bindings == {"source": "session.time_left"}


def test_manifest_parses_connector_games_with_detect_names(tmp_path: Path) -> None:
    plugin_dir = tmp_path / "game_connector"
    plugin_dir.mkdir(parents=True)
    (plugin_dir / "manifest.toml").write_text(
        "\n".join(
            [
                "[plugin]",
                'id = "game_connector"',
                'type = "connector"',
                'version = "1.0.0"',
                'author = "Test"',
                'description = "connector"',
                "",
                "[[connector.game]]",
                'id = "lmu"',
                'detect_names = ["Le Mans Ultimate"]',
                "",
                "[[connector.game]]",
                'id = "rf2"',
                'detect_names = ["rFactor2", "rFactor2 Mod Mode", "rFactor2 Dedicated"]',
                "",
                "[connector_service]",
                'module = "plugins.game_connector.plugin"',
                'class = "GameConnector"',
                "",
            ]
        ),
        encoding="utf-8",
    )

    manifest = load_plugin_manifest(plugin_dir / "manifest.toml")

    assert [game.id for game in manifest.connector_games] == ["lmu", "rf2"]
    assert manifest.connector_games[0].detect_names == ["Le Mans Ultimate"]
    assert manifest.connector_games[1].detect_names == ["rFactor2", "rFactor2 Mod Mode", "rFactor2 Dedicated"]


def test_detect_active_game_id_matches_process_names_with_or_without_exe() -> None:
    manifest = load_plugin_manifest(
        Path(__file__).resolve().parents[2] / "plugins" / "LMU_RF2_Connector" / "manifest.toml"
    )

    assert detect_active_game_id(manifest.connector_games, process_names=["Le Mans Ultimate.exe"]) == "lmu"
    assert detect_active_game_id(manifest.connector_games, process_names=["rFactor2"]) == "rf2"
    assert detect_active_game_id(manifest.connector_games, process_names=["rFactor2 Dedicated.exe"]) == "rf2"
    assert detect_active_game_id(manifest.connector_games, process_names=["not-a-game.exe"]) is None


def test_runtime_boot_can_select_overlay_as_active_ui_plugin(tmp_path: Path) -> None:
    _clear_widget_api_test_modules()
    source_root = tmp_path / "src"
    plugins_dir = source_root / "plugins"
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"

    (plugins_dir / "tinyui").mkdir(parents=True)
    (plugins_dir / "__init__.py").write_text("", encoding="utf-8")
    (plugins_dir / "tinyui" / "plugin.py").write_text("def activate(ctx):\n    return None\n", encoding="utf-8")
    (plugins_dir / "tinyui" / "manifest.toml").write_text(
        "\n".join(
            [
                "[plugin]",
                'id = "tinyui"',
                'type = "host"',
                'version = "1.0.0"',
                'author = "Test"',
                'description = "host"',
                "",
                "[[window]]",
                'id = "tinyui.main"',
                'title = "TinyUi"',
                'surface = "app_main/qml/surface.qml"',
                "",
            ]
        ),
        encoding="utf-8",
    )

    (plugins_dir / "overlay_test_connector_ok").mkdir(parents=True)
    (plugins_dir / "overlay_test_connector_ok" / "__init__.py").write_text("", encoding="utf-8")
    (plugins_dir / "overlay_test_connector_ok" / "plugin.py").write_text(
        "\n".join(
            [
                "class OverlayTestConnector:",
                "    def inspect_snapshot(self):",
                "        return [",
                "            ('session.time_left', '120.0'),",
                "            ('track.name', 'Le Mans'),",
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
    (plugins_dir / "overlay_test_connector_ok" / "manifest.toml").write_text(
        "\n".join(
            [
                "[plugin]",
                'id = "overlay_test_connector_ok"',
                'type = "connector"',
                'version = "1.0.0"',
                'author = "Test"',
                'description = "connector"',
                "",
                "[connector_service]",
                'module = "plugins.overlay_test_connector_ok.plugin"',
                'class = "OverlayTestConnector"',
                "",
            ]
        ),
        encoding="utf-8",
    )

    (plugins_dir / "demo_overlay").mkdir(parents=True)
    (plugins_dir / "demo_overlay" / "__init__.py").write_text("", encoding="utf-8")
    (plugins_dir / "demo_overlay" / "manifest.toml").write_text(
        "\n".join(
            [
                "[plugin]",
                'id = "demo_overlay"',
                'type = "overlay"',
                'version = "1.0.0"',
                'author = "Test"',
                'description = "overlay"',
                'requires = ["overlay_test_connector_ok"]',
                "",
                "[[widget]]",
                'id = "session_time_left"',
                'widget = "textWidget"',
                'label = "Time Left"',
                'bindings = { source = "session.time_left" }',
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

    runtime = Runtime(EventBus())
    runtime.paths = paths
    runtime.settings = SettingsRegistry(config_dir)

    runtime._boot_runtime()
    runtime._apply_initial_runtime_state()

    assert runtime.active_plugin == "demo_overlay"
    assert runtime.get_plugin_state("demo_overlay").name.lower() == "active"
    assert runtime.get_plugin_state("overlay_test_connector_ok").name.lower() == "active"


def test_runtime_rejects_overlay_with_unknown_widget(tmp_path: Path) -> None:
    _clear_widget_api_test_modules()
    source_root = tmp_path / "src"
    plugins_dir = source_root / "plugins"
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"

    (plugins_dir / "tinyui").mkdir(parents=True)
    (plugins_dir / "__init__.py").write_text("", encoding="utf-8")
    (plugins_dir / "tinyui" / "plugin.py").write_text("def activate(ctx):\n    return None\n", encoding="utf-8")
    (plugins_dir / "tinyui" / "manifest.toml").write_text(
        "\n".join(
            [
                "[plugin]",
                'id = "tinyui"',
                'type = "host"',
                'version = "1.0.0"',
                'author = "Test"',
                'description = "host"',
                "",
                "[[window]]",
                'id = "tinyui.main"',
                'title = "TinyUi"',
                'surface = "app_main/qml/surface.qml"',
                "",
            ]
        ),
        encoding="utf-8",
    )

    (plugins_dir / "broken_overlay").mkdir(parents=True)
    (plugins_dir / "broken_overlay" / "__init__.py").write_text("", encoding="utf-8")
    (plugins_dir / "broken_overlay" / "manifest.toml").write_text(
        "\n".join(
            [
                "[plugin]",
                'id = "broken_overlay"',
                'type = "overlay"',
                'version = "1.0.0"',
                'author = "Test"',
                'description = "overlay"',
                "",
                "[[widget]]",
                'id = "broken"',
                'widget = "missingWidget"',
                'bindings = { source = "session.time_left" }',
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

    runtime = Runtime(EventBus())
    runtime.paths = paths
    runtime.settings = SettingsRegistry(config_dir)

    with pytest.raises(ValueError, match="unknown widgets"):
        runtime._boot_runtime()


def test_runtime_rejects_overlay_widget_without_required_binding(tmp_path: Path) -> None:
    _clear_widget_api_test_modules()
    source_root = tmp_path / "src"
    plugins_dir = source_root / "plugins"
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"

    (plugins_dir / "tinyui").mkdir(parents=True)
    (plugins_dir / "__init__.py").write_text("", encoding="utf-8")
    (plugins_dir / "tinyui" / "plugin.py").write_text("def activate(ctx):\n    return None\n", encoding="utf-8")
    (plugins_dir / "tinyui" / "manifest.toml").write_text(
        "\n".join(
            [
                "[plugin]",
                'id = "tinyui"',
                'type = "host"',
                'version = "1.0.0"',
                'author = "Test"',
                'description = "host"',
                "",
                "[[window]]",
                'id = "tinyui.main"',
                'title = "TinyUi"',
                'surface = "app_main/qml/surface.qml"',
                "",
            ]
        ),
        encoding="utf-8",
    )

    (plugins_dir / "broken_overlay").mkdir(parents=True)
    (plugins_dir / "broken_overlay" / "__init__.py").write_text("", encoding="utf-8")
    (plugins_dir / "broken_overlay" / "manifest.toml").write_text(
        "\n".join(
            [
                "[plugin]",
                'id = "broken_overlay"',
                'type = "overlay"',
                'version = "1.0.0"',
                'author = "Test"',
                'description = "overlay"',
                "",
                "[[widget]]",
                'id = "broken"',
                'widget = "textWidget"',
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

    runtime = Runtime(EventBus())
    runtime.paths = paths
    runtime.settings = SettingsRegistry(config_dir)

    with pytest.raises(ValueError, match="missing bindings"):
        runtime._boot_runtime()


def test_runtime_marks_overlay_error_when_binding_key_is_not_supplied(tmp_path: Path) -> None:
    _clear_widget_api_test_modules()
    source_root = tmp_path / "src"
    plugins_dir = source_root / "plugins"
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"

    (plugins_dir / "tinyui").mkdir(parents=True)
    (plugins_dir / "__init__.py").write_text("", encoding="utf-8")
    (plugins_dir / "tinyui" / "plugin.py").write_text("def activate(ctx):\n    return None\n", encoding="utf-8")
    (plugins_dir / "tinyui" / "manifest.toml").write_text(
        "\n".join(
            [
                "[plugin]",
                'id = "tinyui"',
                'type = "host"',
                'version = "1.0.0"',
                'author = "Test"',
                'description = "host"',
                "",
                "[[window]]",
                'id = "tinyui.main"',
                'title = "TinyUi"',
                'surface = "app_main/qml/surface.qml"',
                "",
            ]
        ),
        encoding="utf-8",
    )

    (plugins_dir / "overlay_test_connector_missing").mkdir(parents=True)
    (plugins_dir / "overlay_test_connector_missing" / "__init__.py").write_text("", encoding="utf-8")
    (plugins_dir / "overlay_test_connector_missing" / "plugin.py").write_text(
        "\n".join(
            [
                "class OverlayTestConnector:",
                "    def inspect_snapshot(self):",
                "        return [('session.time_left', '120.0')]",
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
    (plugins_dir / "overlay_test_connector_missing" / "manifest.toml").write_text(
        "\n".join(
            [
                "[plugin]",
                'id = "overlay_test_connector_missing"',
                'type = "connector"',
                'version = "1.0.0"',
                'author = "Test"',
                'description = "connector"',
                "",
                "[connector_service]",
                'module = "plugins.overlay_test_connector_missing.plugin"',
                'class = "OverlayTestConnector"',
                "",
            ]
        ),
        encoding="utf-8",
    )

    (plugins_dir / "broken_overlay").mkdir(parents=True)
    (plugins_dir / "broken_overlay" / "__init__.py").write_text("", encoding="utf-8")
    (plugins_dir / "broken_overlay" / "manifest.toml").write_text(
        "\n".join(
            [
                "[plugin]",
                'id = "broken_overlay"',
                'type = "overlay"',
                'version = "1.0.0"',
                'author = "Test"',
                'description = "overlay"',
                'requires = ["overlay_test_connector_missing"]',
                "",
                "[[widget]]",
                'id = "track_name"',
                'widget = "textWidget"',
                'bindings = { source = "track.name" }',
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

    runtime = Runtime(EventBus())
    runtime.paths = paths
    runtime.settings = SettingsRegistry(config_dir)

    runtime._boot_runtime()
    runtime._apply_initial_runtime_state()

    assert runtime.get_plugin_state("overlay_test_connector_missing").name.lower() == "active"
    assert runtime.get_plugin_state("broken_overlay").name.lower() == "error"


def test_runtime_projects_ready_widget_records_for_active_overlay(tmp_path: Path) -> None:
    _clear_widget_api_test_modules()
    source_root = tmp_path / "src"
    plugins_dir = source_root / "plugins"
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"

    (plugins_dir / "tinyui").mkdir(parents=True)
    (plugins_dir / "__init__.py").write_text("", encoding="utf-8")
    (plugins_dir / "tinyui" / "plugin.py").write_text("def activate(ctx):\n    return None\n", encoding="utf-8")
    (plugins_dir / "tinyui" / "manifest.toml").write_text(
        "\n".join(
            [
                "[plugin]",
                'id = "tinyui"',
                'type = "host"',
                'version = "1.0.0"',
                'author = "Test"',
                'description = "host"',
                "",
                "[[window]]",
                'id = "tinyui.main"',
                'title = "TinyUi"',
                'surface = "app_main/qml/surface.qml"',
                "",
            ]
        ),
        encoding="utf-8",
    )

    (plugins_dir / "record_connector").mkdir(parents=True)
    (plugins_dir / "record_connector" / "__init__.py").write_text("", encoding="utf-8")
    (plugins_dir / "record_connector" / "plugin.py").write_text(
        "\n".join(
            [
                "class RecordConnector:",
                "    def inspect_snapshot(self):",
                "        return [('session.time_left', '120.0 s')]",
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
    (plugins_dir / "record_connector" / "manifest.toml").write_text(
        "\n".join(
            [
                "[plugin]",
                'id = "record_connector"',
                'type = "connector"',
                'version = "1.0.0"',
                'author = "Test"',
                'description = "connector"',
                "",
                "[connector_service]",
                'module = "plugins.record_connector.plugin"',
                'class = "RecordConnector"',
                "",
            ]
        ),
        encoding="utf-8",
    )

    (plugins_dir / "demo_overlay").mkdir(parents=True)
    (plugins_dir / "demo_overlay" / "__init__.py").write_text("", encoding="utf-8")
    (plugins_dir / "demo_overlay" / "manifest.toml").write_text(
        "\n".join(
            [
                "[plugin]",
                'id = "demo_overlay"',
                'type = "overlay"',
                'version = "1.0.0"',
                'author = "Test"',
                'description = "overlay"',
                'requires = ["record_connector"]',
                "",
                "[[widget]]",
                'id = "session_time_left"',
                'widget = "textWidget"',
                'label = "Time Left"',
                'bindings = { source = "session.time_left" }',
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

    runtime = Runtime(EventBus())
    runtime.paths = paths
    runtime.settings = SettingsRegistry(config_dir)
    runtime._boot_runtime()
    runtime._apply_initial_runtime_state()

    records = runtime.active_overlay_widget_records()

    assert len(records) == 1
    assert records[0].overlay_id == "demo_overlay"
    assert records[0].widget_id == "session_time_left"
    assert records[0].status == WidgetRuntimeStatus.READY
    assert records[0].connector_ids == ("record_connector",)


def test_runtime_projects_idle_widget_records_for_inactive_overlay(tmp_path: Path) -> None:
    _clear_widget_api_test_modules()
    source_root = tmp_path / "src"
    plugins_dir = source_root / "plugins"
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"

    (plugins_dir / "tinyui").mkdir(parents=True)
    (plugins_dir / "__init__.py").write_text("", encoding="utf-8")
    (plugins_dir / "tinyui" / "plugin.py").write_text("def activate(ctx):\n    return None\n", encoding="utf-8")
    (plugins_dir / "tinyui" / "manifest.toml").write_text(
        "\n".join(
            [
                "[plugin]",
                'id = "tinyui"',
                'type = "host"',
                'version = "1.0.0"',
                'author = "Test"',
                'description = "host"',
                "",
                "[[window]]",
                'id = "tinyui.main"',
                'title = "TinyUi"',
                'surface = "app_main/qml/surface.qml"',
                "",
            ]
        ),
        encoding="utf-8",
    )

    (plugins_dir / "demo_overlay").mkdir(parents=True)
    (plugins_dir / "demo_overlay" / "__init__.py").write_text("", encoding="utf-8")
    (plugins_dir / "demo_overlay" / "manifest.toml").write_text(
        "\n".join(
            [
                "[plugin]",
                'id = "demo_overlay"',
                'type = "overlay"',
                'version = "1.0.0"',
                'author = "Test"',
                'description = "overlay"',
                "",
                "[[widget]]",
                'id = "session_time_left"',
                'widget = "textWidget"',
                'bindings = { source = "session.time_left" }',
                "",
            ]
        ),
        encoding="utf-8",
    )

    (plugins_dir / "ui_plugin").mkdir(parents=True)
    (plugins_dir / "ui_plugin" / "__init__.py").write_text("", encoding="utf-8")
    (plugins_dir / "ui_plugin" / "plugin.py").write_text("def activate(ctx):\n    return None\n", encoding="utf-8")
    (plugins_dir / "ui_plugin" / "manifest.toml").write_text(
        "\n".join(
            [
                "[plugin]",
                'id = "ui_plugin"',
                'type = "plugin"',
                'version = "1.0.0"',
                'author = "Test"',
                'description = "plugin"',
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

    runtime = Runtime(EventBus())
    runtime.paths = paths
    runtime.settings = SettingsRegistry(config_dir)
    runtime._boot_runtime()
    runtime._apply_initial_runtime_state()
    runtime.set_active_plugin("ui_plugin")

    records = runtime.overlay_widget_records("demo_overlay")

    assert runtime.active_plugin == "ui_plugin"
    assert len(records) == 1
    assert records[0].status == WidgetRuntimeStatus.IDLE


def test_runtime_projects_waiting_for_connector_records(tmp_path: Path) -> None:
    _clear_widget_api_test_modules()
    source_root = tmp_path / "src"
    plugins_dir = source_root / "plugins"
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"

    (plugins_dir / "tinyui").mkdir(parents=True)
    (plugins_dir / "__init__.py").write_text("", encoding="utf-8")
    (plugins_dir / "tinyui" / "plugin.py").write_text("def activate(ctx):\n    return None\n", encoding="utf-8")
    (plugins_dir / "tinyui" / "manifest.toml").write_text(
        "\n".join(
            [
                "[plugin]",
                'id = "tinyui"',
                'type = "host"',
                'version = "1.0.0"',
                'author = "Test"',
                'description = "host"',
                "",
                "[[window]]",
                'id = "tinyui.main"',
                'title = "TinyUi"',
                'surface = "app_main/qml/surface.qml"',
                "",
            ]
        ),
        encoding="utf-8",
    )

    (plugins_dir / "demo_overlay").mkdir(parents=True)
    (plugins_dir / "demo_overlay" / "__init__.py").write_text("", encoding="utf-8")
    (plugins_dir / "demo_overlay" / "manifest.toml").write_text(
        "\n".join(
            [
                "[plugin]",
                'id = "demo_overlay"',
                'type = "overlay"',
                'version = "1.0.0"',
                'author = "Test"',
                'description = "overlay"',
                'requires = ["record_connector"]',
                "",
                "[[widget]]",
                'id = "session_time_left"',
                'widget = "textWidget"',
                'bindings = { source = "session.time_left" }',
                "",
            ]
        ),
        encoding="utf-8",
    )

    (plugins_dir / "record_connector").mkdir(parents=True)
    (plugins_dir / "record_connector" / "__init__.py").write_text("", encoding="utf-8")
    (plugins_dir / "record_connector" / "plugin.py").write_text(
        "\n".join(
            [
                "class RecordConnector:",
                "    def inspect_snapshot(self):",
                "        return [('session.time_left', '120.0 s')]",
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
    (plugins_dir / "record_connector" / "manifest.toml").write_text(
        "\n".join(
            [
                "[plugin]",
                'id = "record_connector"',
                'type = "connector"',
                'version = "1.0.0"',
                'author = "Test"',
                'description = "connector"',
                "",
                "[connector_service]",
                'module = "plugins.record_connector.plugin"',
                'class = "RecordConnector"',
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

    runtime = Runtime(EventBus())
    runtime.paths = paths
    runtime.settings = SettingsRegistry(config_dir)
    runtime._boot_runtime()
    runtime._active_plugin = "demo_overlay"

    records = runtime.overlay_widget_records("demo_overlay")

    assert len(records) == 1
    assert records[0].status == WidgetRuntimeStatus.WAITING_FOR_CONNECTOR


def test_runtime_projects_error_widget_records_when_source_is_unavailable(tmp_path: Path) -> None:
    _clear_widget_api_test_modules()
    source_root = tmp_path / "src"
    plugins_dir = source_root / "plugins"
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"

    (plugins_dir / "tinyui").mkdir(parents=True)
    (plugins_dir / "__init__.py").write_text("", encoding="utf-8")
    (plugins_dir / "tinyui" / "plugin.py").write_text("def activate(ctx):\n    return None\n", encoding="utf-8")
    (plugins_dir / "tinyui" / "manifest.toml").write_text(
        "\n".join(
            [
                "[plugin]",
                'id = "tinyui"',
                'type = "host"',
                'version = "1.0.0"',
                'author = "Test"',
                'description = "host"',
                "",
                "[[window]]",
                'id = "tinyui.main"',
                'title = "TinyUi"',
                'surface = "app_main/qml/surface.qml"',
                "",
            ]
        ),
        encoding="utf-8",
    )

    (plugins_dir / "record_connector").mkdir(parents=True)
    (plugins_dir / "record_connector" / "__init__.py").write_text("", encoding="utf-8")
    (plugins_dir / "record_connector" / "plugin.py").write_text(
        "\n".join(
            [
                "class RecordConnector:",
                "    def inspect_snapshot(self):",
                "        return [('track.name', 'Le Mans')]",
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
    (plugins_dir / "record_connector" / "manifest.toml").write_text(
        "\n".join(
            [
                "[plugin]",
                'id = "record_connector"',
                'type = "connector"',
                'version = "1.0.0"',
                'author = "Test"',
                'description = "connector"',
                "",
                "[connector_service]",
                'module = "plugins.record_connector.plugin"',
                'class = "RecordConnector"',
                "",
            ]
        ),
        encoding="utf-8",
    )

    (plugins_dir / "demo_overlay").mkdir(parents=True)
    (plugins_dir / "demo_overlay" / "__init__.py").write_text("", encoding="utf-8")
    (plugins_dir / "demo_overlay" / "manifest.toml").write_text(
        "\n".join(
            [
                "[plugin]",
                'id = "demo_overlay"',
                'type = "overlay"',
                'version = "1.0.0"',
                'author = "Test"',
                'description = "overlay"',
                'requires = ["record_connector"]',
                "",
                "[[widget]]",
                'id = "session_time_left"',
                'widget = "textWidget"',
                'bindings = { source = "session.time_left" }',
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

    runtime = Runtime(EventBus())
    runtime.paths = paths
    runtime.settings = SettingsRegistry(config_dir)
    runtime._boot_runtime()
    runtime._ensure_plugin_import_roots()
    register_connector_service(
        plugins=runtime._plugins,
        connector_services=runtime.connector_services,
        events=runtime.events,
        plugin_id="record_connector",
    )
    runtime._active_plugin = "demo_overlay"

    records = runtime.overlay_widget_records("demo_overlay")

    assert len(records) == 1
    assert records[0].status == WidgetRuntimeStatus.ERROR
    assert "session.time_left" in records[0].error_message


def test_runtime_projects_waiting_for_game_when_supported_game_is_not_running(tmp_path: Path, monkeypatch) -> None:
    _clear_widget_api_test_modules()
    source_root = tmp_path / "src"
    plugins_dir = source_root / "plugins"
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"

    (plugins_dir / "tinyui").mkdir(parents=True)
    (plugins_dir / "__init__.py").write_text("", encoding="utf-8")
    (plugins_dir / "tinyui" / "plugin.py").write_text("def activate(ctx):\n    return None\n", encoding="utf-8")
    (plugins_dir / "tinyui" / "manifest.toml").write_text(
        "\n".join(
            [
                "[plugin]",
                'id = "tinyui"',
                'type = "host"',
                'version = "1.0.0"',
                'author = "Test"',
                'description = "host"',
                "",
                "[[window]]",
                'id = "tinyui.main"',
                'title = "TinyUi"',
                'surface = "app_main/qml/surface.qml"',
                "",
            ]
        ),
        encoding="utf-8",
    )

    (plugins_dir / "game_connector").mkdir(parents=True)
    (plugins_dir / "game_connector" / "__init__.py").write_text("", encoding="utf-8")
    (plugins_dir / "game_connector" / "plugin.py").write_text(
        "\n".join(
            [
                "class GameConnector:",
                "    def active_game(self):",
                "        return 'none'",
                "",
                "    def inspect_snapshot(self):",
                "        return [('session.time_left', '120.0 s')]",
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
    (plugins_dir / "game_connector" / "manifest.toml").write_text(
        "\n".join(
            [
                "[plugin]",
                'id = "game_connector"',
                'type = "connector"',
                'version = "1.0.0"',
                'author = "Test"',
                'description = "connector"',
                "",
                "[[connector.game]]",
                'id = "lmu"',
                'detect_names = ["Le Mans Ultimate"]',
                "",
                "[connector_service]",
                'module = "plugins.game_connector.plugin"',
                'class = "GameConnector"',
                "",
            ]
        ),
        encoding="utf-8",
    )

    (plugins_dir / "demo_overlay").mkdir(parents=True)
    (plugins_dir / "demo_overlay" / "__init__.py").write_text("", encoding="utf-8")
    (plugins_dir / "demo_overlay" / "manifest.toml").write_text(
        "\n".join(
            [
                "[plugin]",
                'id = "demo_overlay"',
                'type = "overlay"',
                'version = "1.0.0"',
                'author = "Test"',
                'description = "overlay"',
                'requires = ["game_connector"]',
                "",
                "[[widget]]",
                'id = "session_time_left"',
                'widget = "textWidget"',
                'bindings = { source = "session.time_left" }',
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

    runtime = Runtime(EventBus())
    runtime.paths = paths
    runtime.settings = SettingsRegistry(config_dir)
    runtime._boot_runtime()
    runtime._ensure_plugin_import_roots()
    register_connector_service(
        plugins=runtime._plugins,
        connector_services=runtime.connector_services,
        events=runtime.events,
        plugin_id="game_connector",
    )
    runtime._active_plugin = "demo_overlay"
    monkeypatch.setattr(
        "runtime.widgets.projection.detect_active_game_id",
        lambda connector_games: None,
    )

    records = runtime.overlay_widget_records("demo_overlay")

    assert len(records) == 1
    assert records[0].status == WidgetRuntimeStatus.WAITING_FOR_GAME
