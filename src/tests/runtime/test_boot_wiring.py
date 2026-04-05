"""Unit tests for boot-time capability wiring helpers."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any, cast

import pytest

import boot
from app_schema.ui import AppManifest, ChromePolicy
from runtime.runtime import Runtime
from runtime.widgets import WidgetRuntimeRecord, WidgetRuntimeStatus
from runtime_schema import EventBus, EventType, WidgetRuntimeUpdatedData


def _runtime_stub() -> object:
    return SimpleNamespace(
        paths=object(),
        settings=object(),
        connector_services=object(),
        active_overlay_widget_records=lambda: [],
    )


def _shared_capabilities() -> boot.SharedCapabilities:
    return boot.SharedCapabilities(
        menus=object(),
        statusbar=object(),
        plugin_selection=object(),
        plugin_selection_actions=object(),
        tabs=object(),
        connector_read=object(),
        connector_actions=object(),
    )


def _runtime_capabilities() -> boot.RuntimeCapabilities:
    return boot.RuntimeCapabilities(
        plugin_read=object(),
        plugin_state=object(),
        plugin_state_write=object(),
        settings_read=object(),
        settings_write=object(),
        widget_read=object(),
    )


def test_create_runtime_capabilities_requires_booted_runtime() -> None:
    """Runtime-backed capabilities should only be created after BOOT_INIT."""
    runtime = Runtime(EventBus())

    with pytest.raises(AssertionError, match="BOOT_INIT"):
        boot.create_runtime_capabilities(runtime, runtime.events)


def test_create_runtime_capabilities_wires_settings_write_to_settings_read(monkeypatch) -> None:
    """SettingsWrite should be connected to the SettingsRead instance it refreshes."""
    runtime = cast(Runtime, _runtime_stub())
    event_bus = EventBus()
    created: dict[str, object] = {}

    monkeypatch.setattr(boot, "PluginRead", lambda runtime: "plugin_read")
    monkeypatch.setattr(boot, "PluginStateRead", lambda runtime, event_bus: "plugin_state")
    monkeypatch.setattr(boot, "PluginStateWrite", lambda runtime: "plugin_state_write")

    def _fake_settings_read(runtime):
        created["settings_read_runtime"] = runtime
        return "settings_read"

    def _fake_settings_write(runtime, settings_read):
        created["settings_write_runtime"] = runtime
        created["settings_write_read"] = settings_read
        return "settings_write"

    monkeypatch.setattr(boot, "SettingsRead", _fake_settings_read)
    monkeypatch.setattr(boot, "SettingsWrite", _fake_settings_write)
    monkeypatch.setattr(boot, "WidgetRead", lambda runtime, event_bus: "widget_read")

    capabilities = boot.create_runtime_capabilities(runtime, event_bus)

    assert capabilities.settings_read == "settings_read"
    assert capabilities.settings_write == "settings_write"
    assert capabilities.widget_read == "widget_read"
    assert created == {
        "settings_read_runtime": runtime,
        "settings_write_runtime": runtime,
        "settings_write_read": "settings_read",
    }


def test_build_window_capability_properties_omits_tabs_for_non_tab_windows() -> None:
    """Only windows with a tab bar should receive the tabs capability."""
    manifest = AppManifest(
        id="devtools.main",
        title="DevTools",
        chrome=ChromePolicy(show_tab_bar=False),
    )

    properties = boot.build_window_capability_properties(
        manifest,
        _shared_capabilities(),
        _runtime_capabilities(),
    )

    assert "tabs" not in properties
    assert "pluginRead" in properties
    assert "widgetRead" in properties
    assert "connectorRead" in properties


def test_build_window_capability_properties_includes_tabs_for_tab_windows() -> None:
    """Tabbed windows should receive the shared tabs capability."""
    shared = _shared_capabilities()
    manifest = AppManifest(
        id="tinyui.main",
        title="TinyUI",
        chrome=ChromePolicy(show_tab_bar=True),
    )

    properties = boot.build_window_capability_properties(
        manifest,
        shared,
        _runtime_capabilities(),
    )

    assert properties["tabs"] is shared.tabs


def test_create_widget_window_host_syncs_current_runtime_records(monkeypatch) -> None:
    """Widget window host should receive the current overlay widget records at startup."""

    created: dict[str, object] = {}
    connected: list[object] = []
    records = [
        WidgetRuntimeRecord(
            overlay_id="demo_overlay",
            widget_id="session_time_left",
            widget_type="textWidget",
            label="Time Left",
            source="session.time_left",
            status=WidgetRuntimeStatus.READY,
            connector_ids=("LMU_RF2_Connector",),
        )
    ]

    class _FakeSignal:
        def connect(self, callback) -> None:
            connected.append(callback)

    class _FakeApp:
        def __init__(self) -> None:
            self.aboutToQuit = _FakeSignal()
            self.properties: dict[str, object] = {}

        def setProperty(self, key: str, value: object) -> None:
            self.properties[key] = value

    class _FakeHost:
        def __init__(self) -> None:
            created["host"] = self

        def sync_records(self, runtime_records) -> None:
            created["records"] = runtime_records

        def close_all(self) -> None:
            created["closed"] = True

    class _RuntimeStub:
        def active_overlay_widget_records(self):
            return records

    runtime = _RuntimeStub()
    app = _FakeApp()
    event_bus = EventBus()

    monkeypatch.setattr(boot, "WidgetWindowHost", _FakeHost)

    host = boot.create_widget_window_host(app, event_bus, runtime)

    assert host is created["host"]
    assert created["records"] is records
    assert host.close_all in connected
    assert "_widgetWindowHostController" in app.properties
    assert "_widgetRuntimePoller" in app.properties


def test_widget_window_host_resyncs_on_runtime_events(monkeypatch) -> None:
    """Relevant runtime events should trigger another host sync."""

    sync_calls: list[object] = []
    records = [
        WidgetRuntimeRecord(
            overlay_id="demo_overlay",
            widget_id="session_time_left",
            widget_type="textWidget",
            label="Time Left",
            source="session.time_left",
            status=WidgetRuntimeStatus.READY,
            connector_ids=("LMU_RF2_Connector",),
        )
    ]

    class _FakeSignal:
        def connect(self, callback) -> None:
            self.callback = callback

    class _FakeApp:
        def __init__(self) -> None:
            self.aboutToQuit = _FakeSignal()
            self.properties: dict[str, object] = {}

        def setProperty(self, key: str, value: object) -> None:
            self.properties[key] = value

    class _FakeHost:
        def sync_records(self, runtime_records) -> None:
            sync_calls.append(runtime_records)

        def close_all(self) -> None:
            return None

    class _RuntimeStub:
        def active_overlay_widget_records(self):
            return records

    event_bus = EventBus()
    app = _FakeApp()
    runtime = _RuntimeStub()

    monkeypatch.setattr(boot, "WidgetWindowHost", _FakeHost)

    boot.create_widget_window_host(app, event_bus, runtime)
    event_bus.emit_typed(
        EventType.WIDGET_RUNTIME_UPDATED,
        WidgetRuntimeUpdatedData(reason="test"),
    )

    assert sync_calls == [records, records]
