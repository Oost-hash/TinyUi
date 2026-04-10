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
from runtimeV2.ui.capabilities.chrome_model_read import UIChromeModelRead
from runtimeV2.ui.capabilities.window_actions_write import WindowActionsWrite
from runtimeV2.ui.capabilities.window_records_read import WindowRecordsRead
from runtimeV2.ui.chrome_model import build_ui_chrome_model
from runtimeV2.contracts import UIWindowStatus
from runtimeV2.ui.projection import project_ui_window_records
from runtimeV2.ui.readiness import determine_render_status
from runtimeV2.ui.schemas.manifest import AppManifest, ChromePolicy, MenuItem, StatusbarItemDecl, TabDecl, UiManifest


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
                        menu=[MenuItem(label="Settings", action="open:settings.main")],
                        statusbar=[StatusbarItemDecl(text="Ready", side="left")],
                    )
                ],
                tabs=[
                    TabDecl(
                        id="tinyui.widgets",
                        label="Widgets",
                        target="tinyui.main",
                        surface=Path("widgets.qml"),
                        plugin_id="tinyui",
                    )
                ],
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
                windows=[AppManifest(id="devtools.main", title="DevTools", surface=Path("devtools.qml"))],
                tabs=[
                    TabDecl(
                        id="devtools.tab",
                        label="DevTools",
                        target="tinyui.main",
                        surface=Path("devtools_tab.qml"),
                        plugin_id="devtools",
                    )
                ],
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
                menu=[MenuItem(label="Settings", action="open:settings.main")],
                statusbar=[StatusbarItemDecl(text="Ready", side="left")],
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


def test_window_records_read_exposes_projected_ui_records() -> None:
    """Window read capability should stay a thin wrapper around UI records."""

    records = project_ui_window_records(
        ui_manifest_read=ManifestUiRead(_manifest_registry()),
        main_window_read=_main_window_read(),
    )
    capability = WindowRecordsRead(records)

    assert capability.window_record("tinyui.main") == records[0]
    assert capability.all_window_records() == records


def test_ui_chrome_model_read_projects_tabs_menu_and_active_plugin() -> None:
    """Chrome model read should expose the host-facing UI chrome projection."""

    class _FakeActiveRead:
        def get_active_plugin(self) -> str | None:
            return "devtools"

    model = build_ui_chrome_model(
        main_window_read=_main_window_read(),
        ui_manifest_read=ManifestUiRead(_manifest_registry()),
        active_read=cast(Any, _FakeActiveRead()),
    )
    capability = UIChromeModelRead(model)

    assert [tab.tab_id for tab in capability.tabs()] == ["tinyui.widgets", "devtools.tab"]
    assert capability.menu_items()[0].label == "Settings"
    assert capability.statusbar_items()[0].text == "Ready"
    assert capability.chrome_model().active_plugin_id == "devtools"


def test_window_actions_write_exposes_openable_non_main_windows() -> None:
    """UI window actions should validate openable non-main window ids."""

    records = project_ui_window_records(
        ui_manifest_read=ManifestUiRead(_manifest_registry()),
        main_window_read=_main_window_read(),
    )
    capability = WindowActionsWrite(WindowRecordsRead(records), "tinyui.main")

    assert capability.main_window_id() == "tinyui.main"
    assert capability.openable_window_ids() == ["devtools.main", "broken.dialog"]
    assert capability.can_open_window("devtools.main") is True
    assert capability.can_open_window("tinyui.main") is False
    assert capability.request_open_window("devtools.main") is True
    assert capability.request_open_window("tinyui.main") is False
