"""Unit tests for runtime-owned window records."""

from __future__ import annotations

from pathlib import Path
from typing import Any, cast

from app_schema.plugin import PluginManifest
from app_schema.ui import AppManifest, UiManifest
from runtime.ui import WindowRuntimeStatus, project_window_records
from runtime.runtime import Runtime
from runtime_schema import EventBus, EventType


def _plugins() -> dict[str, PluginManifest]:
    host_window = AppManifest(id="tinyui.main", title="TinyUI", surface=Path("host.qml"))
    devtools_window = AppManifest(id="devtools.main", title="DevTools", surface=Path("devtools.qml"))
    dialog_window = AppManifest(id="dummy.dialog", title="Dummy Dialog", surface=Path("dialog.qml"))
    return {
        "tinyui": PluginManifest(
            plugin_id="tinyui",
            plugin_type="host",
            version="",
            author="",
            description="",
            icon="",
            requires=[],
            settings=[],
            ui=UiManifest(windows=[host_window]),
        ),
        "devtools": PluginManifest(
            plugin_id="devtools",
            plugin_type="plugin",
            version="",
            author="",
            description="",
            icon="",
            requires=[],
            settings=[],
            ui=UiManifest(windows=[devtools_window]),
        ),
        "dummy_plugin": PluginManifest(
            plugin_id="dummy_plugin",
            plugin_type="plugin",
            version="",
            author="",
            description="",
            icon="",
            requires=[],
            settings=[],
            ui=UiManifest(windows=[dialog_window]),
        ),
    }


def test_project_window_records_marks_main_window_role() -> None:
    """Projected runtime records should identify the host main window."""

    records = project_window_records(_plugins(), window_states={}, window_errors={})

    assert [(record.window_id, record.window_role, record.status.value) for record in records] == [
        ("tinyui.main", "main", "idle"),
        ("devtools.main", "window", "idle"),
        ("dummy.dialog", "dialog", "idle"),
    ]


def test_runtime_begin_shutdown_marks_open_windows_closing() -> None:
    """Runtime shutdown should project open windows into the closing state."""

    runtime = Runtime(EventBus())
    cast(Any, runtime)._plugins = _plugins()
    runtime.mark_window_open("tinyui.main")
    runtime.mark_window_open("devtools.main")

    runtime.begin_shutdown()

    assert runtime.window_record("tinyui.main") is not None
    assert runtime.window_record("tinyui.main").status == WindowRuntimeStatus.CLOSING  # type: ignore[union-attr]
    assert runtime.window_record("devtools.main").status == WindowRuntimeStatus.CLOSING  # type: ignore[union-attr]
    assert runtime.active_overlay_widget_records() == []


def test_runtime_emits_window_runtime_updates() -> None:
    """Window state writes should emit a typed runtime update event."""

    bus = EventBus()
    runtime = Runtime(bus)
    cast(Any, runtime)._plugins = _plugins()

    runtime.mark_window_opening("tinyui.main")

    events = bus.get_history(EventType.WINDOW_RUNTIME_UPDATED)
    assert len(events) == 1
    assert events[0].data.reason == "opening"


def test_runtime_begin_shutdown_emits_typed_shutdown_event() -> None:
    """Shutdown should emit a typed runtime shutdown event once."""

    bus = EventBus()
    runtime = Runtime(bus)
    cast(Any, runtime)._plugins = _plugins()

    runtime.begin_shutdown("test_close")
    runtime.begin_shutdown("second_call_should_be_ignored")

    events = bus.get_history(EventType.RUNTIME_SHUTDOWN)
    assert len(events) == 1
    assert events[0].data.reason == "test_close"
