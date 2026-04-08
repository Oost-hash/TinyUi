"""Regression tests for runtime V2 UI window projection."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast

from runtimeV2.host.capabilities.main_window_read import MainWindowRead
from runtimeV2.host.contracts import HostAppIdentity, HostShell
from runtimeV2.manifest.capabilities.ui_read import ManifestUiRead
from runtimeV2.manifest.registry import ManifestRegistry
from runtimeV2.plugins.schemas.manifest import PluginManifest
from runtimeV2.ui.contracts import UIWindowStatus
from runtimeV2.ui.projection import project_ui_window_records
from runtimeV2.ui.readiness import determine_render_status
from runtimeV2.ui.schemas.manifest import AppManifest, ChromePolicy, UiManifest


def _manifest_registry() -> ManifestRegistry:
    registry = ManifestRegistry()
    registry.register_manifest(
        manifest=PluginManifest(
            plugin_id="tinyui",
            plugin_type="host",
            version="0.5.0",
            author="",
            description="",
            icon="",
            requires=[],
            ui=UiManifest(
                windows=[
                    AppManifest(
                        id="tinyui.main",
                        title="TinyUI",
                        chrome=ChromePolicy(custom_chrome=Path("host_chrome.qml")),
                    )
                ]
            ),
        ),
        manifest_path=Path("tinyui/plugin.toml"),
        resource_root=Path("."),
        source="test",
    )
    registry.register_manifest(
        manifest=PluginManifest(
            plugin_id="devtools",
            plugin_type="plugin",
            version="0.5.0",
            author="",
            description="",
            icon="",
            requires=[],
            ui=UiManifest(
                windows=[
                    AppManifest(
                        id="devtools.main",
                        title="DevTools",
                        surface=Path("devtools.qml"),
                    )
                ]
            ),
        ),
        manifest_path=Path("devtools/plugin.toml"),
        resource_root=Path("."),
        source="test",
    )
    registry.register_manifest(
        manifest=PluginManifest(
            plugin_id="broken_plugin",
            plugin_type="plugin",
            version="0.5.0",
            author="",
            description="",
            icon="",
            requires=[],
            ui=UiManifest(
                windows=[
                    AppManifest(
                        id="broken.dialog",
                        title="Broken",
                    )
                ]
            ),
        ),
        manifest_path=Path("broken/plugin.toml"),
        resource_root=Path("."),
        source="test",
    )
    return registry


def _main_window_read() -> MainWindowRead:
    return MainWindowRead(
        HostShell(
            host_plugin_id="tinyui",
            host_manifest=cast(Any, SimpleNamespace()),
            main_window=AppManifest(
                id="tinyui.main",
                title="TinyUI",
                chrome=ChromePolicy(custom_chrome=Path("host_chrome.qml")),
            ),
            identity=HostAppIdentity(
                app_id="tinyui",
                app_version="0.5.0",
                app_title="TinyUI",
                app_icon="",
            ),
        )
    )


def test_project_ui_window_records_marks_main_window_role() -> None:
    """Projected V2 UI records should identify the host main window and visibility."""

    records = project_ui_window_records(
        ui_manifest_read=ManifestUiRead(_manifest_registry()),
        main_window_read=_main_window_read(),
    )

    assert [(record.window_id, record.window_role, record.visible) for record in records] == [
        ("tinyui.main", "main", True),
        ("devtools.main", "window", False),
        ("broken.dialog", "window", False),
    ]


def test_project_ui_window_records_flags_missing_render_target_as_error() -> None:
    """Windows without surface or custom chrome should be projected as errors."""

    records = project_ui_window_records(
        ui_manifest_read=ManifestUiRead(_manifest_registry()),
        main_window_read=_main_window_read(),
    )

    broken = next(record for record in records if record.window_id == "broken.dialog")

    assert broken.status == UIWindowStatus.ERROR
    assert broken.error_message == "Window has no render target"


def test_determine_render_status_accepts_custom_chrome_for_main_window() -> None:
    """A main window with custom chrome should still be render-ready."""

    records = project_ui_window_records(
        ui_manifest_read=ManifestUiRead(_manifest_registry()),
        main_window_read=_main_window_read(),
    )

    render_status = determine_render_status(
        main_window_read=_main_window_read(),
        records=records,
    )

    assert render_status.render_ready
    assert render_status.main_window_id == "tinyui.main"


def test_determine_render_status_blocks_when_main_window_record_is_missing() -> None:
    """Render readiness should fail when the projected main window record is missing."""

    render_status = determine_render_status(
        main_window_read=_main_window_read(),
        records=[],
    )

    assert not render_status.render_ready
    assert render_status.render_blocker == "Main window record is missing"
