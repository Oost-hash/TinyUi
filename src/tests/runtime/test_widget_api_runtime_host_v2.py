"""Tests for widget_api runtime V2 hosting."""

from __future__ import annotations

from collections.abc import Callable
from types import SimpleNamespace
from typing import Any, cast

from shared_runtime_host.capabilities.widget_host import WidgetHostCapability
from runtimeV2.events.capabilities.event_read import EventRead
from runtimeV2.events.capabilities.event_registration_write import EventRegistrationWrite, EventSubscription
from runtimeV2.events.contracts import EventBus, EventType
from runtimeV2.events.event_registry import EventRegistry
from runtimeV2.events.startup_shutdown.startup import EventsStartupResult
from runtimeV2.persistence.capabilities.widget_config_write import WidgetConfigWrite
from runtimeV2.schemas.startup import StartupResult
from runtimeV2.widgets.capabilities.widget_records_read import WidgetRecordsRead
from runtimeV2.contracts import WidgetRecord, WidgetStatus
from runtimeV2.widgets.store import WidgetRecordsStore
from runtimeV2.widgets.startup_shutdown.startup import WidgetsStartupResult
from shared_runtime_host.register_capabilities import register_event_registration_host, register_widget_host
from shared_runtime_host.registry import SharedRuntimeHostRegistry, create_shared_runtime_host_registry
from shared_runtime_host.capabilities.widget_api import WidgetEffectsQmlCapability, widget_window_data
from widget_api.capabilities import ThresholdCapability
from widget_api.capabilities.threshold import threshold_entries
from widget_api.register_runtime_host import register_widget_runtime_host
from widget_api.runtime_host import create_widget_window_host, start_widget_host
from widget_api.window_host import WidgetWindowHost


class _FakeSignal:
    def __init__(self) -> None:
        self._callbacks: list[Callable[[], None]] = []

    def connect(self, callback) -> None:
        self._callbacks.append(callback)


class _FakeApp:
    def __init__(self) -> None:
        self.aboutToQuit = _FakeSignal()
        self.properties: dict[str, object] = {}

    def setProperty(self, key: str, value: object) -> None:
        self.properties[key] = value


class _FakeWidgetConfigWrite:
    def __init__(self) -> None:
        self.position_calls: list[tuple[str, str, int, int]] = []

    def set_widget_position(self, overlay_id: str, widget_id: str, x: int, y: int) -> bool:
        self.position_calls.append((overlay_id, widget_id, x, y))
        return True

    def set_widget_enabled(self, overlay_id: str, widget_id: str, enabled: bool) -> bool:
        return True

    def set_widget_values(self, overlay_id: str, widget_id: str, values: dict[str, object]) -> bool:
        return True

    def reset_widget_values(self, overlay_id: str, widget_id: str) -> bool:
        return True


class _FakeSchedulerWrite:
    def __init__(self) -> None:
        self.jobs: dict[str, dict[str, object]] = {}

    def register_job(
        self,
        *,
        job_id: str,
        owner_domain: str,
        interval_ms: int,
        callback: Callable[[], object],
        enabled: bool = True,
    ) -> bool:
        self.jobs[job_id] = {
            "owner_domain": owner_domain,
            "interval_ms": interval_ms,
            "callback": callback,
            "enabled": enabled,
        }
        return True


class _FakeRuntime:
    def __init__(self, records: list[WidgetRecord], widget_config_write: object) -> None:
        self._bus = EventBus()
        self._store = WidgetRecordsStore()
        self._store.set_records(records)
        self._widgets = WidgetsStartupResult(
            store=self._store,
            records=records,
            capabilities=cast(Any, object()),
        )
        registry = EventRegistry()
        self._events = EventsStartupResult(
            bus=self._bus,
            registry=registry,
            event_read=EventRead(registry),
            event_registration_write=EventRegistrationWrite(registry, self._bus),
        )
        self._widget_config_write = widget_config_write
        self.scheduler_write = _FakeSchedulerWrite()
        self.shutdown_calls: list[str] = []

    def domain_result(self, name: str, _result_type: type[Any]) -> Any:
        if name == "events":
            return self._events
        if name == "widgets":
            return self._widgets
        raise KeyError(name)

    def capability(self, name: str, _capability_type: type[Any]) -> Any:
        if name == "widget_config_write":
            return self._widget_config_write
        if name == "widget_records_read":
            return WidgetRecordsRead(self._store)
        if name == "scheduler_write":
            return self.scheduler_write
        if name == "event_registration_write":
            return self._events.event_registration_write
        if name == "shutdown":
            return cast(Any, _FakeShutdown(self.shutdown_calls))
        raise KeyError(name)


class _FakeShutdown:
    def __init__(self, calls: list[str]) -> None:
        self._calls = calls

    def begin_shutdown(self, reason: str = "app_quit") -> bool:
        self._calls.append(reason)
        return True


def _host_registry(runtime: _FakeRuntime) -> SharedRuntimeHostRegistry:
    registry = create_shared_runtime_host_registry(cast(Any, runtime))
    register_event_registration_host(registry)
    register_widget_host(registry)
    register_widget_runtime_host(registry)
    return registry


def test_widget_runtime_host_syncs_runtime_v2_widget_records(monkeypatch) -> None:
    """Widget runtime host should sync the current V2 widget store records."""

    records = [
        WidgetRecord(
            overlay_id="demo_overlay",
            widget_id="speed",
            widget_type="gauge",
            label="Speed",
            source="car.speed",
            bindings={"source": "car.speed"},
            status=WidgetStatus.READY,
            connector_ids=("iracing",),
            enabled=True,
            position=(5, 6),
            values={"units": "kph"},
        )
    ]
    app = _FakeApp()
    runtime = _FakeRuntime(records, _FakeWidgetConfigWrite())
    created: dict[str, object] = {}

    class _FakeHost:
        def __init__(self, _widget_host, _widget_config_write, _widget_effects) -> None:
            created["host"] = self
            created["widget_effects"] = _widget_effects

        def sync_records(self, runtime_records) -> None:
            created["records"] = runtime_records

        def close_all(self) -> None:
            created["closed"] = True

    monkeypatch.setattr("widget_api.runtime_host.WidgetWindowHost", _FakeHost)

    result = create_widget_window_host(app, cast(Any, runtime), _host_registry(runtime))

    assert result.host is created["host"]
    assert created["records"] == records
    assert isinstance(created["widget_effects"], WidgetEffectsQmlCapability)
    assert "_widgetRuntimeHost" in app.properties


def test_widget_runtime_host_waits_for_widget_runtime_update_events(monkeypatch) -> None:
    """The widget_api host should sync records after widgets domain refreshes."""

    records = [
        WidgetRecord(
            overlay_id="demo_overlay",
            widget_id="speed",
            widget_type="gauge",
            label="Speed",
            source="car.speed",
            bindings={"source": "car.speed"},
            status=WidgetStatus.READY,
            connector_ids=("iracing",),
        )
    ]
    app = _FakeApp()
    runtime = _FakeRuntime(records, _FakeWidgetConfigWrite())
    sync_calls: list[list[WidgetRecord]] = []

    class _FakeHost:
        def __init__(self, _widget_host, _widget_config_write, _widget_effects) -> None:
            pass

        def sync_records(self, runtime_records) -> None:
            sync_calls.append(list(runtime_records))

        def close_all(self) -> None:
            return None

    monkeypatch.setattr("widget_api.runtime_host.WidgetWindowHost", _FakeHost)

    create_widget_window_host(app, cast(Any, runtime), _host_registry(runtime))
    runtime.domain_result("events", EventsStartupResult).bus.emit_typed(
        EventType.WIDGET_RUNTIME_UPDATED,
        data=None,
        source="widgets",
    )

    assert sync_calls == [records, records]


def test_start_widget_host_returns_typed_success(monkeypatch) -> None:
    """Widget runtime host startup should return a typed success result."""

    app = _FakeApp()
    runtime = _FakeRuntime([], _FakeWidgetConfigWrite())
    monkeypatch.setattr(
        "widget_api.runtime_host.WidgetWindowHost",
        lambda _widget_host, _widget_config_write, _widget_effects: SimpleNamespace(
            sync_records=lambda _records: None,
            close_all=lambda: None,
        ),
    )

    _result, startup_result = start_widget_host(app, cast(Any, runtime), _host_registry(runtime))

    assert startup_result == StartupResult(ok=True)


def test_widget_runtime_host_closes_on_runtime_shutdown(monkeypatch) -> None:
    """Runtime shutdown should close hosted widget windows through the shared host layer."""

    app = _FakeApp()
    runtime = _FakeRuntime([], _FakeWidgetConfigWrite())
    calls: list[str] = []

    class _FakeHost:
        def __init__(self, _widget_host, _widget_config_write, _widget_effects) -> None:
            pass

        def sync_records(self, _runtime_records) -> None:
            return None

        def close_all(self) -> None:
            calls.append("closed")

    monkeypatch.setattr("widget_api.runtime_host.WidgetWindowHost", _FakeHost)

    create_widget_window_host(app, cast(Any, runtime), _host_registry(runtime))
    runtime.domain_result("events", EventsStartupResult).bus.emit_typed(
        EventType.RUNTIME_SHUTDOWN,
        data=None,
        source="runtime",
    )

    assert calls == ["closed"]


def test_widget_runtime_host_requests_runtime_shutdown_on_app_quit(monkeypatch) -> None:
    """Application quit should request runtime shutdown through the shared host layer."""

    app = _FakeApp()
    runtime = _FakeRuntime([], _FakeWidgetConfigWrite())

    monkeypatch.setattr(
        "widget_api.runtime_host.WidgetWindowHost",
        lambda _widget_host, _widget_config_write, _widget_effects: SimpleNamespace(
            sync_records=lambda _records: None,
            close_all=lambda: None,
        ),
    )

    create_widget_window_host(app, cast(Any, runtime), _host_registry(runtime))
    for callback in app.aboutToQuit._callbacks:
        callback()

    assert runtime.shutdown_calls == ["app_quit"]


def test_widget_runtime_host_closes_event_subscription_on_shutdown(monkeypatch) -> None:
    """Widget runtime host should close its event subscription when the host shuts down."""

    app = _FakeApp()
    runtime = _FakeRuntime([], _FakeWidgetConfigWrite())
    subscription_calls: list[str] = []

    class _FakeSubscription:
        def close(self) -> None:
            subscription_calls.append("closed")

    def _subscribe(*_args, **_kwargs) -> EventSubscription:
        return cast(Any, _FakeSubscription())

    monkeypatch.setattr(
        "shared_runtime_host.events.SharedRuntimeHostEvents.subscribe",
        _subscribe,
    )
    monkeypatch.setattr(
        "widget_api.runtime_host.WidgetWindowHost",
        lambda _widget_host, _widget_config_write, _widget_effects: SimpleNamespace(
            sync_records=lambda _records: None,
            close_all=lambda: None,
        ),
    )

    create_widget_window_host(app, cast(Any, runtime), _host_registry(runtime))
    runtime.domain_result("events", EventsStartupResult).bus.emit_typed(
        EventType.RUNTIME_SHUTDOWN,
        data=None,
        source="runtime",
    )

    assert subscription_calls == ["closed"]


def test_widget_data_adapter_uses_runtime_v2_record_shape() -> None:
    """Widget runtime adapter should shape V2 records for widget window QML."""

    record = WidgetRecord(
        overlay_id="demo_overlay",
        widget_id="speed",
        widget_type="gauge",
        label="Speed",
        source="car.speed",
        bindings={"source": "car.speed"},
        status=WidgetStatus.HIDDEN,
        connector_ids=("iracing",),
        enabled=False,
        position=(12, 34),
        values={"units": "kph"},
    )
    store = WidgetRecordsStore()
    store.set_records([record])

    widget_data = widget_window_data(WidgetHostCapability(WidgetRecordsRead(store)), record)

    assert widget_data["widgetId"] == "speed"
    assert widget_data["overlayId"] == "demo_overlay"
    assert widget_data["bindings"] == {"source": "car.speed"}
    assert widget_data["values"] == {"units": "kph"}
    assert widget_data["visible"] is False
    assert widget_data["x"] == 12
    assert widget_data["y"] == 34
    assert "widgetEffects" not in widget_data


def test_widget_data_adapter_formats_ready_values_from_widget_values() -> None:
    """Widget host projection should restore v0.4.0-style display formatting."""

    record = WidgetRecord(
        overlay_id="demo_overlay",
        widget_id="fuel",
        widget_type="textWidget",
        label="Fuel",
        source="vehicle.fuel",
        bindings={"source": "vehicle.fuel"},
        status=WidgetStatus.READY,
        connector_ids=("LMU_RF2_Connector",),
        values={"format": "{:.1f} L"},
        resolved_value="1.50",
    )
    store = WidgetRecordsStore()
    store.set_records([record])

    widget_data = widget_window_data(WidgetHostCapability(WidgetRecordsRead(store)), record)

    assert widget_data["displayText"] == "1.5 L"


def test_widget_window_host_updates_data_without_resetting_position() -> None:
    """Existing widget windows should not receive an empty widgetData during refresh."""

    initial = WidgetRecord(
        overlay_id="demo_overlay",
        widget_id="speed",
        widget_type="gauge",
        label="Speed",
        source="car.speed",
        bindings={"source": "car.speed"},
        status=WidgetStatus.READY,
        connector_ids=("iracing",),
        position=(120, 240),
    )
    updated = WidgetRecord(
        overlay_id="demo_overlay",
        widget_id="speed",
        widget_type="gauge",
        label="Speed",
        source="car.speed",
        bindings={"source": "car.speed"},
        status=WidgetStatus.READY,
        connector_ids=("iracing",),
        position=(120, 240),
        resolved_value="123",
    )
    store = WidgetRecordsStore()
    store.set_records([updated])

    class _FakeEffects:
        def __init__(self) -> None:
            self.updated: list[dict[str, object]] = []

        def update_widget(self, widget_data: dict[str, object]) -> None:
            self.updated.append(widget_data)

        def remove_widget(self, _overlay_id: str, _widget_id: str) -> None:
            return None

    class _FakeWindow:
        def __init__(self) -> None:
            self.properties: list[tuple[str, object]] = []
            self.visible_calls: list[bool] = []

        def setProperty(self, name: str, value: object) -> None:
            self.properties.append((name, value))

        def setVisible(self, visible: bool) -> None:
            self.visible_calls.append(visible)

    host = WidgetWindowHost.__new__(WidgetWindowHost)
    cast(Any, host)._widget_host = WidgetHostCapability(WidgetRecordsRead(store))
    cast(Any, host)._widget_effects = _FakeEffects()
    fake_window = _FakeWindow()
    cast(Any, host)._windows = {
        "demo_overlay:speed": SimpleNamespace(
            record=initial,
            window=fake_window,
            widget_data=widget_window_data(cast(Any, host)._widget_host, initial),
        ),
    }

    host.sync_records([updated])

    assert fake_window.properties == [
        ("widgetData", widget_window_data(cast(Any, host)._widget_host, updated)),
    ]
    assert fake_window.visible_calls == [True]


def test_widget_window_host_ignores_position_only_refreshes() -> None:
    """Existing widget windows should not receive full data updates for position-only refreshes."""

    initial = WidgetRecord(
        overlay_id="demo_overlay",
        widget_id="speed",
        widget_type="gauge",
        label="Speed",
        source="car.speed",
        bindings={"source": "car.speed"},
        status=WidgetStatus.READY,
        connector_ids=("iracing",),
        position=(120, 240),
        resolved_value="123",
    )
    updated = WidgetRecord(
        overlay_id="demo_overlay",
        widget_id="speed",
        widget_type="gauge",
        label="Speed",
        source="car.speed",
        bindings={"source": "car.speed"},
        status=WidgetStatus.READY,
        connector_ids=("iracing",),
        position=(320, 480),
        resolved_value="123",
    )
    store = WidgetRecordsStore()
    store.set_records([updated])

    class _FakeEffects:
        def update_widget(self, _widget_data: dict[str, object]) -> None:
            return None

        def remove_widget(self, _overlay_id: str, _widget_id: str) -> None:
            return None

    class _FakeWindow:
        def __init__(self) -> None:
            self.properties: list[tuple[str, object]] = []
            self.visible_calls: list[bool] = []

        def setProperty(self, name: str, value: object) -> None:
            self.properties.append((name, value))

        def setVisible(self, visible: bool) -> None:
            self.visible_calls.append(visible)

    host = WidgetWindowHost.__new__(WidgetWindowHost)
    cast(Any, host)._widget_host = WidgetHostCapability(WidgetRecordsRead(store))
    cast(Any, host)._widget_effects = _FakeEffects()
    fake_window = _FakeWindow()
    cast(Any, host)._windows = {
        "demo_overlay:speed": SimpleNamespace(
            record=initial,
            window=fake_window,
            widget_data=widget_window_data(cast(Any, host)._widget_host, initial),
        ),
    }

    host.sync_records([updated])

    assert fake_window.properties == []
    assert fake_window.visible_calls == [True]


def test_threshold_capability_uses_upper_bound_rules() -> None:
    """Threshold rules should select the first sorted upper bound."""

    thresholds = threshold_entries(
        [
            {"value": 10, "color": "#FFB000", "flash": True, "flash_speed": 2, "flash_target": "text"},
            {
                "value": 2,
                "color": "#FF4040",
                "colorTarget": "border",
                "flash": True,
                "flashSpeed": 1,
                "flashTarget": "border",
            },
        ]
    )
    capability = ThresholdCapability()

    critical = capability.evaluate(thresholds, 1.5)
    warning = capability.evaluate(thresholds, 5.0)
    inactive = capability.evaluate(thresholds, 20.0)

    assert critical.active is True
    assert critical.color == "#FF4040"
    assert critical.color_target == "border"
    assert critical.flash is True
    assert critical.flash_speed == 1
    assert critical.flash_target == "border"
    assert warning.active is True
    assert warning.color == "#FFB000"
    assert warning.color_target == "value"
    assert warning.flash_target == "text"
    assert inactive.active is False


def test_widget_effects_adapter_uses_persisted_threshold_values() -> None:
    """Widget effects should expose persisted threshold flash state to QML."""

    scheduler_write = _FakeSchedulerWrite()
    effects = WidgetEffectsQmlCapability(cast(Any, scheduler_write))

    effects.update_widget(
        {
            "overlayId": "demo_overlay",
            "widgetId": "fuel",
            "resolvedValue": "1.5",
            "displayText": "1.5",
            "values": {
                "thresholds": [
                    {
                        "value": 2,
                        "color": "#FF4040",
                        "colorTarget": "border",
                        "flash": True,
                        "flashSpeed": 1,
                        "flashTarget": "border",
                    }
                ]
            },
        }
    )

    assert scheduler_write.jobs["widget_api.effects.flash"]["owner_domain"] == "widget_api"
    assert effects.textColor("demo_overlay", "fuel", "#E0E0E0") == "#FF4040"
    assert effects.colorTarget("demo_overlay", "fuel") == "border"
    assert effects.flashTarget("demo_overlay", "fuel") == "border"
    assert effects.flashVisible("demo_overlay", "fuel") is True

    effects.tick()

    assert effects.flashVisible("demo_overlay", "fuel") is False

