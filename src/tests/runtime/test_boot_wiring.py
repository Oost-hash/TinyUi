"""Unit tests for boot-time capability wiring helpers."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any, Callable, cast

import pytest

import boot
from app_schema.ui import AppManifest, ChromePolicy
from capabilities import window_capabilities
from capabilities.window_capabilities import RuntimeCapabilities, SharedCapabilities
from runtime.runtime import Runtime
from runtime_schema import StartupResult, StartupStep, run_startup_pipeline
from runtime.widgets import WidgetRuntimeRecord, WidgetRuntimeStatus
from runtime_schema import EventBus, EventType, WidgetRuntimeUpdatedData
from ui_api.startup import open_main_runtime_window, register_runtime_window_actions
from ui_api.ui_runtime_host import WindowHostController, attach_main_window_shutdown, attach_window_runtime_tracking, start_window_host
from widget_api.runtime_host import create_widget_window_host, start_widget_host


def _runtime_stub() -> object:
    return SimpleNamespace(
        paths=object(),
        settings=object(),
        connector_services=object(),
        window_records=lambda: [],
        active_overlay_widget_records=lambda: [],
    )


def _shared_capabilities() -> SharedCapabilities:
    return SharedCapabilities(
        menus=object(),
        statusbar=object(),
        plugin_selection=object(),
        plugin_selection_actions=object(),
        tabs=object(),
        connector_read=object(),
        connector_actions=object(),
    )


def _runtime_capabilities() -> RuntimeCapabilities:
    return RuntimeCapabilities(
        plugin_read=object(),
        plugin_state=object(),
        plugin_state_write=object(),
        settings_read=object(),
        settings_write=object(),
        window_read=object(),
        widget_read=object(),
    )


def test_create_runtime_capabilities_requires_booted_runtime(
    booted_runtime: Runtime,
) -> None:
    """Runtime-backed capabilities should only be created after BOOT_INIT."""
    # booted_runtime fixture already emitted BOOT_INIT, so we need a fresh runtime
    # that hasn't been booted to test the error case
    from runtime.persistence import startup_persistence, get_persistence_result
    from runtime.events import startup_events, get_events_result
    
    event_bus = EventBus()
    persistence_result = startup_persistence(event_bus)
    if not persistence_result.ok:
        pytest.skip("Persistence startup failed")
    persistence = get_persistence_result()
    if persistence is None:
        pytest.skip("Persistence not available")
        
    unbooted_runtime = Runtime(
        event_bus=event_bus,
        settings=persistence.settings,
        widget_store=persistence.widget_store,
        config_manager=persistence.config_manager,
    )

    with pytest.raises(AssertionError, match="BOOT_INIT"):
        boot.create_runtime_capabilities(unbooted_runtime, unbooted_runtime.events)


def test_run_startup_pipeline_stops_at_first_error() -> None:
    """The startup coordinator should stop when one startup step fails."""

    calls: list[str] = []

    result = run_startup_pipeline([
        StartupStep("first", lambda: calls.append("first") or StartupResult(ok=True, error_message="")),
        StartupStep("second", lambda: calls.append("second") or StartupResult(ok=False, error_message="broken")),
        StartupStep("third", lambda: calls.append("third") or StartupResult(ok=True, error_message="")),
    ])

    assert calls == ["first", "second"]
    assert result == StartupResult(ok=False, error_message="broken")


def test_create_runtime_capabilities_wires_settings_write_to_settings_read(monkeypatch) -> None:
    """SettingsWrite should be connected to the SettingsRead instance it refreshes."""
    runtime = cast(Runtime, _runtime_stub())
    event_bus = EventBus()
    created: dict[str, object] = {}

    monkeypatch.setattr(window_capabilities, "PluginRead", lambda runtime: "plugin_read")
    monkeypatch.setattr(window_capabilities, "PluginStateRead", lambda runtime, event_bus: "plugin_state")
    monkeypatch.setattr(window_capabilities, "PluginStateWrite", lambda runtime: "plugin_state_write")

    def _fake_settings_read(runtime):
        created["settings_read_runtime"] = runtime
        return "settings_read"

    def _fake_settings_write(runtime, settings_read):
        created["settings_write_runtime"] = runtime
        created["settings_write_read"] = settings_read
        return "settings_write"

    monkeypatch.setattr(window_capabilities, "SettingsRead", _fake_settings_read)
    monkeypatch.setattr(window_capabilities, "SettingsWrite", _fake_settings_write)
    monkeypatch.setattr(window_capabilities, "WidgetRead", lambda runtime, event_bus: "widget_read")

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
    assert "windowRead" in properties
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

    monkeypatch.setattr("widget_api.runtime_host.WidgetWindowHost", _FakeHost)

    host = create_widget_window_host(app, event_bus, runtime)

    assert host is created["host"]
    assert created["records"] is records
    assert host.close_all in connected
    assert "_widgetWindowHostController" in app.properties
    assert "_widgetRuntimePoller" in app.properties


def test_start_widget_host_returns_ok_result(monkeypatch) -> None:
    """Widget host startup should return a typed success result."""

    class _FakeApp:
        def __init__(self) -> None:
            self.aboutToQuit = SimpleNamespace(connect=lambda _callback: None)
            self.properties: dict[str, object] = {}

        def setProperty(self, key: str, value: object) -> None:
            self.properties[key] = value

    class _RuntimeStub:
        def active_overlay_widget_records(self):
            return []

    monkeypatch.setattr("widget_api.runtime_host.WidgetWindowHost", lambda: SimpleNamespace(sync_records=lambda _records: None, close_all=lambda: None))

    _host, result = start_widget_host(_FakeApp(), EventBus(), _RuntimeStub())

    assert result == StartupResult(ok=True, error_message="")


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

    monkeypatch.setattr("widget_api.runtime_host.WidgetWindowHost", _FakeHost)

    create_widget_window_host(app, event_bus, runtime)
    event_bus.emit_typed(
        EventType.WIDGET_RUNTIME_UPDATED,
        WidgetRuntimeUpdatedData(reason="test"),
    )

    assert sync_calls == [records, records]


def test_open_main_runtime_window_marks_runtime_window_open(monkeypatch) -> None:
    """Opening the main runtime window should write opening and open state back to runtime."""

    runtime_calls: list[tuple[str, str]] = []

    class _RuntimeStub:
        paths = object()
        settings = object()
        connector_services = object()

        def main_window(self):
            return AppManifest(id="tinyui.main", title="TinyUI", surface=None)

        def mark_window_opening(self, window_id: str) -> None:
            runtime_calls.append(("opening", window_id))

        def mark_window_open(self, window_id: str) -> None:
            runtime_calls.append(("open", window_id))

    monkeypatch.setattr("ui_api.startup.resolve_plugin_panel", lambda engine, runtime: ("", None))
    monkeypatch.setattr("ui_api.startup.open_window", lambda *args, **kwargs: SimpleNamespace(qml_window=SimpleNamespace()))

    manifest, _handle, result = open_main_runtime_window(
        app=object(),
        engine=object(),
        actions=cast(Any, object()),
        theme=cast(Any, object()),
        runtime=cast(Runtime, _RuntimeStub()),
        shared_capabilities=_shared_capabilities(),
        runtime_capabilities=_runtime_capabilities(),
        build_window_capability_properties=boot.build_window_capability_properties,
    )

    assert manifest is not None
    assert result == StartupResult(ok=True, error_message="")
    assert runtime_calls == [("opening", "tinyui.main"), ("open", "tinyui.main")]


def test_register_runtime_window_actions_marks_main_window_closing(monkeypatch) -> None:
    """The close action should request runtime shutdown before closing the main window."""

    close_calls: list[tuple[str, str]] = []
    registered: dict[str, object] = {}

    class _DestroyedSignal:
        def connect(self, _callback) -> None:
            return None

    class _WindowStub:
        def __init__(self) -> None:
            self.destroyed = _DestroyedSignal()

        def setProperty(self, *_args) -> None:
            return None

        def close(self) -> None:
            close_calls.append(("qt", "tinyui.main"))

    class _RuntimeStub:
        def window_for(self, _window_id: str):
            return None

        def all_windows(self):
            return []

        def mark_window_closing(self, window_id: str) -> None:
            close_calls.append(("closing", window_id))

        def mark_window_closed(self, _window_id: str) -> None:
            return None

        def mark_window_opening(self, _window_id: str) -> None:
            return None

        def mark_window_open(self, _window_id: str) -> None:
            return None

        def mark_window_error(self, _window_id: str, _message: str) -> None:
            return None

        def window_records(self):
            return []

        def begin_shutdown(self, reason: str = "app_quit") -> None:
            close_calls.append(("shutdown", reason))

    class _ActionsStub:
        def register(self, action: str, callback) -> None:
            registered[action] = callback

    class _AppStub:
        def quit(self) -> None:
            return None

    main_handle = SimpleNamespace(qml_window=_WindowStub())
    actions = _ActionsStub()
    window_host_controller = SimpleNamespace(track=lambda *_args: None)

    result = register_runtime_window_actions(
        app=_AppStub(),
        engine=object(),
        actions=cast(Any, actions),
        theme=cast(Any, object()),
        runtime=cast(Runtime, _RuntimeStub()),
        shared_capabilities=_shared_capabilities(),
        runtime_capabilities=_runtime_capabilities(),
        main_manifest=AppManifest(id="tinyui.main", title="TinyUI"),
        main_handle=main_handle,
        window_host_controller=cast(Any, window_host_controller),
        build_window_capability_properties=boot.build_window_capability_properties,
    )

    cast(Callable[[], None], registered["close"])()

    assert result == StartupResult(ok=True, error_message="")
    assert close_calls == [("shutdown", "main_window_close"), ("qt", "tinyui.main")]


def test_window_runtime_tracking_marks_closed_when_window_hides() -> None:
    """A window becoming invisible should update runtime state to closed."""

    calls: list[tuple[str, str]] = []

    class _Signal:
        def __init__(self) -> None:
            self._callbacks: list[Callable[..., None]] = []

        def connect(self, callback) -> None:
            self._callbacks.append(callback)

        def emit(self, *args) -> None:
            for callback in self._callbacks:
                callback(*args)

    class _WindowStub:
        def __init__(self) -> None:
            self.destroyed = _Signal()
            self.visibleChanged = _Signal()

    class _RuntimeStub:
        def mark_window_open(self, window_id: str) -> None:
            calls.append(("open", window_id))

        def mark_window_closed(self, window_id: str) -> None:
            calls.append(("closed", window_id))

    window = _WindowStub()
    runtime = _RuntimeStub()

    attach_window_runtime_tracking(cast(Any, runtime), "dummy.dialog", window)
    window.visibleChanged.emit(False)

    assert calls == [("closed", "dummy.dialog")]


def test_main_window_shutdown_starts_when_main_window_hides() -> None:
    """Hiding the main window via the native close affordance should request shutdown."""

    calls: list[tuple[str, str]] = []

    class _Signal:
        def __init__(self) -> None:
            self._callbacks: list[Callable[..., None]] = []

        def connect(self, callback) -> None:
            self._callbacks.append(callback)

        def emit(self, *args) -> None:
            for callback in self._callbacks:
                callback(*args)

    class _WindowStub:
        def __init__(self) -> None:
            self.destroyed = _Signal()
            self.visibleChanged = _Signal()

    class _RuntimeStub:
        def begin_shutdown(self, reason: str = "app_quit") -> None:
            calls.append(("shutdown", reason))

    window = _WindowStub()
    runtime = _RuntimeStub()

    attach_main_window_shutdown(cast(Any, runtime), window)
    window.visibleChanged.emit(False)

    assert calls == [("shutdown", "main_window_hidden")]


def test_start_window_host_returns_ok_result() -> None:
    """Window host startup should return a typed success result."""

    _controller, result = start_window_host(EventBus())

    assert isinstance(_controller, WindowHostController)
    assert result == StartupResult(ok=True, error_message="")


def test_window_host_controller_closes_tracked_windows_on_shutdown() -> None:
    """Runtime shutdown should close all tracked application windows."""

    closed: list[str] = []

    class _WindowStub:
        def __init__(self, window_id: str) -> None:
            self.window_id = window_id

        def close(self) -> None:
            closed.append(self.window_id)

    event_bus = EventBus()
    controller = WindowHostController(event_bus)
    controller.attach()
    controller.track("tinyui.main", SimpleNamespace(qml_window=_WindowStub("tinyui.main")))
    controller.track("dummy.dialog", SimpleNamespace(qml_window=_WindowStub("dummy.dialog")))

    event_bus.emit_typed(EventType.RUNTIME_SHUTDOWN, None)

    assert closed == ["tinyui.main", "dummy.dialog"]
