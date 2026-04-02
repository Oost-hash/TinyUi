"""Tests for host-window contribution rules."""

from __future__ import annotations

from pathlib import Path

import pytest

from runtime.manifest import load_plugin_manifest


def test_host_plugin_must_declare_a_window(tmp_path: Path) -> None:
    """The host must still provide the primary application window."""
    plugin_dir = tmp_path / "tinyui"
    plugin_dir.mkdir(parents=True)
    (plugin_dir / "manifest.toml").write_text(
        "\n".join(
            [
                "[plugin]",
                'id = "tinyui"',
                'type = "host"',
                'version = "1.0.0"',
                'author = "Test"',
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Host plugin must declare at least one window"):
        load_plugin_manifest(plugin_dir / "manifest.toml")


def test_host_first_window_is_the_main_window(tmp_path: Path) -> None:
    """The first host window becomes the primary application window."""
    plugin_dir = tmp_path / "tinyui"
    plugin_dir.mkdir(parents=True)
    (plugin_dir / "manifest.toml").write_text(
        "\n".join(
            [
                "[plugin]",
                'id = "tinyui"',
                'type = "host"',
                'version = "1.0.0"',
                'author = "Test"',
                "",
                "[[window]]",
                'id = "tinyui.main"',
                'title = "TinyUI"',
                'surface = "app_main/qml/surface.qml"',
                "",
                "[[window]]",
                'id = "settings.main"',
                'title = "Settings"',
                'surface = "app_settings/qml/surface.qml"',
            ]
        ),
        encoding="utf-8",
    )

    manifest = load_plugin_manifest(plugin_dir / "manifest.toml")

    assert manifest.plugin_type == "host"
    assert manifest.windows[0].id == "tinyui.main"
    assert manifest.windows[1].id == "settings.main"
