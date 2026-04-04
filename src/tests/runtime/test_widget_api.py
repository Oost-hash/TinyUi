from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest

from runtime.app.paths import AppPaths
from runtime.manifest import load_plugin_manifest
from runtime.persistence import SettingsRegistry
from runtime.runtime import Runtime
from runtime_schema import EventBus
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
