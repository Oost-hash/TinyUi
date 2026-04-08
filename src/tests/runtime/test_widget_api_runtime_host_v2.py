"""Tests for widget_api runtime V2 hosting."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any, cast

from runtime_host.capabilities.widget_host import WidgetHostCapability
from runtimeV2.events.capabilities.event_read import EventRead
from runtimeV2.events.contracts import EventBus, EventType
from runtimeV2.events.event_registry import EventRegistry
from runtimeV2.events.startup import EventsStartupResult
from runtimeV2.persistence.capabilities.widget_config_write import WidgetConfigWrite
from runtimeV2.schemas.startup import StartupResult
from runtimeV2.widgets.capabilities.widget_records_read import WidgetRecordsRead
from runtimeV2.widgets.contracts import WidgetRecord, WidgetStatus
from runtimeV2.widgets.store import WidgetRecordsStore
from runtimeV2.widgets.startup import WidgetsStartupResult
from widget_api.runtime_adapters import widget_data_for_record
from widget_api.runtime_host import create_widget_window_host, start_widget_host


class _FakeSignal:
    def __init__(self) -> None:
        self._callbacks: list[object] = []

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


class _FakePoller:
    def __init__(self) -> None:
        self.refresh_calls = 0

    def refresh(self) -> list[WidgetRecord]:
        self.refresh_calls += 1
        return []


class _FakeRuntime:
    def __init__(self, records: list[WidgetRecord], widget_config_write: object) -> None:
        self._bus = EventBus()
        self._store = WidgetRecordsStore()
        self._store.set_records(records)
        self._widgets = WidgetsStartupResult(
            store=self._store,
            records=records,
            poller=cast(Any, _FakePoller()),
            capabilities=cast(Any, object()),
        )
        self._events = EventsStartupResult(
            bus=self._bus,
            registry=EventRegistry(),
            event_read=EventRead(EventRegistry()),
        )
        self._widget_config_write = widget_config_write

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
        raise KeyError(name)


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
        def __init__(self, _widget_host, _widget_config_write) -> None:
            created["host"] = self

        def sync_records(self, runtime_records) -> None:
            created["records"] = runtime_records

        def close_all(self) -> None:
            created["closed"] = True

    monkeypatch.setattr("widget_api.runtime_host.WidgetWindowHost", _FakeHost)

    result = create_widget_window_host(app, cast(Any, runtime))

    assert result.host is created["host"]
    assert created["records"] == records
    assert "_widgetRuntimeHost" in app.properties


def test_widget_runtime_host_refreshes_on_connector_events(monkeypatch) -> None:
    """Connector changes should refresh widgets through the V2 widgets poller."""

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
        def __init__(self, _widget_host, _widget_config_write) -> None:
            pass

        def sync_records(self, runtime_records) -> None:
            sync_calls.append(list(runtime_records))

        def close_all(self) -> None:
            return None

    monkeypatch.setattr("widget_api.runtime_host.WidgetWindowHost", _FakeHost)

    create_widget_window_host(app, cast(Any, runtime))
    runtime.domain_result("events", EventsStartupResult).bus.emit_typed(
        EventType.CONNECTOR_SERVICE_UPDATED,
        data=None,
        source="connectors",
    )

    assert sync_calls == [records, records]
    assert cast(_FakePoller, runtime.domain_result("widgets", WidgetsStartupResult).poller).refresh_calls == 1


def test_start_widget_host_returns_typed_success(monkeypatch) -> None:
    """Widget runtime host startup should return a typed success result."""

    app = _FakeApp()
    runtime = _FakeRuntime([], _FakeWidgetConfigWrite())
    monkeypatch.setattr(
        "widget_api.runtime_host.WidgetWindowHost",
        lambda _widget_host, _widget_config_write: SimpleNamespace(sync_records=lambda _records: None, close_all=lambda: None),
    )

    _result, startup_result = start_widget_host(app, cast(Any, runtime))

    assert startup_result == StartupResult(ok=True)


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

    widget_data = widget_data_for_record(WidgetHostCapability(WidgetRecordsRead(store)), record)

    assert widget_data["widgetId"] == "speed"
    assert widget_data["overlayId"] == "demo_overlay"
    assert widget_data["bindings"] == {"source": "car.speed"}
    assert widget_data["values"] == {"units": "kph"}
    assert widget_data["visible"] is False
    assert widget_data["x"] == 12
    assert widget_data["y"] == 34
