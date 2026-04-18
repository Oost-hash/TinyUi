"""Tests for runtime V2 widgets."""

from __future__ import annotations

from typing import Any, cast

from runtimeV2.persistence.capabilities.widget_config_write import WidgetConfigWrite
from runtimeV2.connectors.capabilities.connector_read import ConnectorRead
from runtimeV2.contracts import ConnectorGameStateDecision
from runtimeV2.connectors.decision_store import ConnectorGameStateDecisionStore
from runtimeV2.connectors.service_registry import ConnectorServiceRegistry
from runtimeV2.events.contracts import EventBus, EventType
from runtimeV2.manifest.capabilities.connector_read import ManifestConnectorRead
from runtimeV2.manifest.capabilities.overlay_read import ManifestOverlayRead
from runtimeV2.manifest.parser import load_plugin_manifest
from runtimeV2.connectors.schemas.manifest import ConnectorManifest
from runtimeV2.connectors.schemas.manifest import ConnectorServiceDecl
from runtimeV2.persistence.capabilities.widget_config_read import WidgetConfigRead
from runtimeV2.persistence.backends import JsonTestPersistenceBackend
from runtimeV2.persistence.registry import PersistenceRegistry
from runtimeV2.persistence.repository import PersistenceRepository
from runtimeV2.persistence.startup_shutdown.register_persistence import register_persistence_document_schemas
from runtimeV2.persistence.widget_config import WidgetConfigStore
from runtimeV2.plugins.capabilities.active_read import PluginActiveRead
from runtimeV2.scheduler.capabilities.scheduler_clock_read import SchedulerClockRead
from runtimeV2.scheduler.capabilities.scheduler_clock_write import SchedulerClockWrite
from runtimeV2.scheduler.capabilities.scheduler_write import SchedulerWrite
from runtimeV2.scheduler.clock import SchedulerClock
from runtimeV2.scheduler.driver import SchedulerDriver
from runtimeV2.scheduler.registry import SchedulerRegistry
from runtimeV2.widgets.capabilities.widget_records_read import WidgetRecordsRead
from runtimeV2.widgets.capabilities.widget_records_refresh import WidgetRecordsRefresh
from runtimeV2.widgets.capabilities.widget_refresh_policy import WidgetRefreshPolicy
from runtimeV2.widgets.capabilities.widget_visibility_read import WidgetVisibilityRead
from runtimeV2.widgets.capabilities.widget_visibility_write import WidgetVisibilityWrite
from runtimeV2.contracts import WidgetStatus, WidgetVisibilityChangedData
from runtimeV2.widgets.store import WidgetRecordsStore
from runtimeV2.widgets.visibility_focus import WidgetVisibilityFocus
from runtimeV2.widgets.schemas.manifest import OverlayManifest, OverlayWidgetDecl, WidgetDefaults
from runtimeV2.widgets.startup_shutdown.register_persistence import register_widget_persistence_schemas


def _json_backend(tmp_path) -> JsonTestPersistenceBackend:
    return JsonTestPersistenceBackend()


def _repository(tmp_path) -> PersistenceRepository:
    registry = PersistenceRegistry()
    register_persistence_document_schemas(registry)
    register_widget_persistence_schemas(registry)
    return PersistenceRepository(registry, _json_backend(tmp_path))


class _FakeOverlayRead:
    def __init__(self, declarations: dict[str, OverlayManifest]) -> None:
        self._declarations = declarations

    def overlay_declarations(self) -> dict[str, OverlayManifest]:
        return dict(self._declarations)


class _FakeConnectorDeclRead:
    def __init__(self, declarations: dict[str, ConnectorManifest]) -> None:
        self._declarations = declarations

    def connector_declarations(self) -> dict[str, ConnectorManifest]:
        return dict(self._declarations)


class _FakeActiveRead:
    def __init__(self, plugin_id: str | None) -> None:
        self._plugin_id = plugin_id

    def get_active_plugin(self) -> str | None:
        return self._plugin_id


class _FakeConnectorService:
    def __init__(self, snapshot: list[tuple[str, str]], *, active_source: str = "mock") -> None:
        self._snapshot = snapshot
        self._active_source = active_source

    def inspect_snapshot(self) -> list[tuple[str, str]]:
        return list(self._snapshot)

    def active_source(self) -> str:
        return self._active_source

    def active_game(self) -> str:
        return "none" if self._active_source in {"none", "mock"} else self._active_source


def _widget_config_read(tmp_path, overlay_id: str, widget_id: str) -> WidgetConfigRead:
    store = WidgetConfigStore(_repository(tmp_path))
    store.set_widget_enabled(overlay_id, widget_id, False)
    store.set_widget_position(overlay_id, widget_id, 12, 34)
    store.set_widget_values(overlay_id, widget_id, {"units": "kph"})
    return WidgetConfigRead(store)


def _widget_records_refresh(
    *,
    store: WidgetRecordsStore,
    overlay_read,
    connector_decl_read,
    connector_read,
    active_read,
    widget_config_read,
    events: EventBus,
    visibility_read=None,
) -> WidgetRecordsRefresh:
    return WidgetRecordsRefresh(
        store=store,
        overlay_read=overlay_read,
        connector_decl_read=connector_decl_read,
        connector_read=connector_read,
        active_read=active_read,
        widget_config_read=widget_config_read,
        events=events,
        visibility_read=visibility_read,
    )


def test_widget_records_refresh_merges_config_and_emits_update(tmp_path) -> None:
    """Widget refresh should merge widget config into widget runtime records."""

    overlay_id = "demo_overlay"
    widget_id = "speed"
    store = WidgetRecordsStore()
    bus = EventBus()
    refresh = _widget_records_refresh(
        store=store,
        overlay_read=_FakeOverlayRead(
            {
                overlay_id: OverlayManifest(
                    connectors=["iracing"],
                    widgets=[
                        OverlayWidgetDecl(
                            id=widget_id,
                            widget="gauge",
                            label="Speed",
                            bindings={"source": "car.speed"},
                            defaults=WidgetDefaults(enabled=True, position=(1, 2)),
                        )
                    ],
                )
            }
        ),
        connector_decl_read=_FakeConnectorDeclRead(
            {
                "iracing": ConnectorManifest(
                    service=ConnectorServiceDecl(module="plugins.iracing", class_name="IRacingService")
                )
            }
        ),
        connector_read=ConnectorRead(ConnectorServiceRegistry()),
        active_read=_FakeActiveRead(overlay_id),
        widget_config_read=_widget_config_read(tmp_path, overlay_id, widget_id),
        events=bus,
    )

    records = refresh.refresh()

    assert len(records) == 1
    record = records[0]
    assert record.bindings == {"source": "car.speed"}
    assert record.enabled is False
    assert record.position == (12, 34)
    assert record.values == {"units": "kph"}
    assert record.status == WidgetStatus.HIDDEN
    assert store.widget_record(overlay_id, widget_id) == record
    assert bus.get_history()[-1].type == EventType.WIDGET_RUNTIME_UPDATED


def test_widget_records_refresh_marks_ready_when_active_and_connected(tmp_path) -> None:
    """Widget refresh should mark widgets ready when connector services are present."""

    overlay_id = "demo_overlay"
    widget_id = "speed"
    connector_services = ConnectorServiceRegistry()
    connector_services.register(
        "iracing",
        "iracing",
        "IRacing",
        _FakeConnectorService([("car.speed", "321 km/h")]),
    )
    widget_config_store = WidgetConfigStore(_repository(tmp_path))
    WidgetConfigWrite(widget_config_store).set_global_widgets_visible(True)
    widget_config = WidgetConfigRead(widget_config_store)
    store = WidgetRecordsStore()
    refresh = _widget_records_refresh(
        store=store,
        overlay_read=_FakeOverlayRead(
            {
                overlay_id: OverlayManifest(
                    connectors=["iracing"],
                    widgets=[OverlayWidgetDecl(id=widget_id, widget="gauge", bindings={"source": "car.speed"})],
                )
            }
        ),
        connector_decl_read=_FakeConnectorDeclRead(
            {
                "iracing": ConnectorManifest(
                    service=ConnectorServiceDecl(module="plugins.iracing", class_name="IRacingService")
                )
            }
        ),
        connector_read=ConnectorRead(connector_services),
        active_read=_FakeActiveRead(overlay_id),
        widget_config_read=widget_config,
        events=EventBus(),
    )

    record = refresh.refresh()[0]

    assert record.status == WidgetStatus.READY
    assert record.enabled is True
    assert record.position == (0, 0)
    assert record.resolved_value == "321 km/h"


def test_widget_records_refresh_includes_manifest_widget_values(tmp_path) -> None:
    """Widget refresh should carry manifest-owned functional defaults into runtime records."""

    overlay_id = "demo_overlay"
    widget_id = "fuel"
    connector_services = ConnectorServiceRegistry()
    connector_services.register(
        "iracing",
        "iracing",
        "IRacing",
        _FakeConnectorService([("vehicle.fuel", "1.50")]),
    )
    widget_config_store = WidgetConfigStore(_repository(tmp_path))
    WidgetConfigWrite(widget_config_store).set_global_widgets_visible(True)
    widget_config = WidgetConfigRead(widget_config_store)
    store = WidgetRecordsStore()
    refresh = _widget_records_refresh(
        store=store,
        overlay_read=_FakeOverlayRead(
            {
                overlay_id: OverlayManifest(
                    connectors=["iracing"],
                    widgets=[
                        OverlayWidgetDecl(
                            id=widget_id,
                            widget="textWidget",
                            bindings={"source": "vehicle.fuel"},
                            values={
                                "format": "{:.1f} L",
                                "thresholds": [
                                    {
                                        "value": 2.0,
                                        "color": "#FF4444",
                                        "flash": True,
                                        "flash_speed": 3,
                                        "flash_target": "value",
                                    }
                                ],
                            },
                        )
                    ],
                )
            }
        ),
        connector_decl_read=_FakeConnectorDeclRead(
            {
                "iracing": ConnectorManifest(
                    service=ConnectorServiceDecl(module="plugins.iracing", class_name="IRacingService")
                )
            }
        ),
        connector_read=ConnectorRead(connector_services),
        active_read=_FakeActiveRead(overlay_id),
        widget_config_read=widget_config,
        events=EventBus(),
    )

    record = refresh.refresh()[0]

    assert record.resolved_value == "1.50"
    assert record.values == {
        "format": "{:.1f} L",
        "thresholds": [
            {
                "value": 2.0,
                "color": "#FF4444",
                "flash": True,
                "flash_speed": 3,
                "flash_target": "value",
            }
        ],
    }


def test_overlay_widget_files_parse_functional_values(tmp_path) -> None:
    """Overlay widget TOML should preserve v0.4.0-style format and threshold defaults."""

    plugin_root = tmp_path / "demo_overlay"
    widgets_dir = plugin_root / "widgets"
    widgets_dir.mkdir(parents=True)
    (plugin_root / "manifest.toml").write_text(
        """
[plugin]
id = "demo_overlay"
type = "overlay"

[overlay]
connectors = ["iracing"]
widgets_dir = "widgets"
""".strip(),
        encoding="utf-8",
    )
    (widgets_dir / "fuel.toml").write_text(
        """
[widget]
id = "fuel"
widget = "textWidget"
title = "Fuel"
description = "Fuel remaining in liters"
label = "Fuel"
format = "{:.1f} L"

[bindings]
source = "vehicle.fuel"

[[thresholds]]
value = 2.0
color = "#FF4444"
flash = true
flash_speed = 3
flash_target = "value"
""".strip(),
        encoding="utf-8",
    )

    manifest = load_plugin_manifest(plugin_root / "manifest.toml")

    assert manifest.overlay is not None
    widget = manifest.overlay.widgets[0]
    assert widget.values == {
        "format": "{:.1f} L",
        "title": "Fuel",
        "description": "Fuel remaining in liters",
        "thresholds": [
            {
                "value": 2.0,
                "color": "#FF4444",
                "flash": True,
                "flash_speed": 3,
                "flash_target": "value",
            }
        ],
    }


def test_widget_records_refresh_allows_persisted_label_override(tmp_path) -> None:
    """Widget refresh should let config values override the manifest display label."""

    overlay_id = "demo_overlay"
    widget_id = "fuel"
    store = WidgetConfigStore(_repository(tmp_path))
    store.set_widget_values(overlay_id, widget_id, {"label": "Fuel Left"})
    refresh = _widget_records_refresh(
        store=WidgetRecordsStore(),
        overlay_read=_FakeOverlayRead(
            {
                overlay_id: OverlayManifest(
                    widgets=[
                        OverlayWidgetDecl(
                            id=widget_id,
                            widget="textWidget",
                            label="Fuel",
                            values={"description": "Fuel remaining in liters"},
                        )
                    ],
                )
            }
        ),
        connector_decl_read=_FakeConnectorDeclRead({}),
        connector_read=ConnectorRead(ConnectorServiceRegistry()),
        active_read=_FakeActiveRead(overlay_id),
        widget_config_read=WidgetConfigRead(store),
        events=EventBus(),
    )

    record = refresh.refresh()[0]

    assert record.label == "Fuel Left"
    assert record.values == {
        "description": "Fuel remaining in liters",
        "label": "Fuel Left",
    }


def test_widget_records_read_exposes_store_projection(tmp_path) -> None:
    """Widget records read should expose the store without adding extra policy."""

    overlay_id = "demo_overlay"
    widget_id = "speed"
    store = WidgetRecordsStore()
    refresh = _widget_records_refresh(
        store=store,
        overlay_read=_FakeOverlayRead(
            {
                overlay_id: OverlayManifest(
                    widgets=[OverlayWidgetDecl(id=widget_id, widget="gauge", bindings={"source": "car.speed"})]
                )
            }
        ),
        connector_decl_read=_FakeConnectorDeclRead({}),
        connector_read=ConnectorRead(ConnectorServiceRegistry()),
        active_read=_FakeActiveRead(None),
        widget_config_read=_widget_config_read(tmp_path, overlay_id, widget_id),
        events=EventBus(),
    )

    refresh.refresh()
    read = WidgetRecordsRead(store)
    record = read.widget_record(overlay_id, widget_id)

    assert record is not None
    assert read.records_for_overlay(overlay_id) == [record]
    assert read.all_widget_records() == [record]


def test_widget_records_refresh_updates_widget_store(tmp_path) -> None:
    """Widget refresh capability should project records into the widgets-owned store."""

    overlay_id = "demo_overlay"
    widget_id = "speed"
    store = WidgetRecordsStore()
    refresh = _widget_records_refresh(
        store=store,
        overlay_read=_FakeOverlayRead(
            {
                overlay_id: OverlayManifest(
                    widgets=[OverlayWidgetDecl(id=widget_id, widget="gauge", bindings={"source": "car.speed"})]
                )
            }
        ),
        connector_decl_read=_FakeConnectorDeclRead({}),
        connector_read=ConnectorRead(ConnectorServiceRegistry()),
        active_read=_FakeActiveRead(None),
        widget_config_read=_widget_config_read(tmp_path, overlay_id, widget_id),
        events=EventBus(),
    )
    records = refresh.refresh()

    assert records == store.all_widget_records()
    assert len(records) == 1


def test_widget_refresh_policy_refreshes_on_connector_updates_when_visible() -> None:
    """Widget refresh policy should use scheduler ticks when the central clock is live."""

    bus = EventBus()
    calls: list[str] = []
    scheduler_registry = SchedulerRegistry()
    scheduler_write = SchedulerWrite(scheduler_registry, SchedulerDriver(scheduler_registry, bus), bus)
    scheduler_clock = SchedulerClock()
    scheduler_clock_write = SchedulerClockWrite(scheduler_clock, bus)

    class _FakeRefresh:
        def refresh(self) -> list[object]:
            calls.append("refresh")
            return []

    class _FakeVisibilityRead:
        def global_visible(self) -> bool:
            return True

    policy = WidgetRefreshPolicy(
        records_refresh=cast(Any, _FakeRefresh()),
        visibility_read=cast(Any, _FakeVisibilityRead()),
        scheduler_write=scheduler_write,
        scheduler_clock_read=SchedulerClockRead(scheduler_clock),
        events=bus,
    )

    policy.attach()
    scheduler_write.tick(0)
    scheduler_clock_write.request_clock_mode("tests", "live")
    scheduler_write.tick(20)

    assert calls == ["refresh"]


def test_widget_refresh_policy_skips_connector_updates_when_hidden() -> None:
    """Widget refresh policy should avoid live refreshes while widgets are hidden."""

    bus = EventBus()
    calls: list[str] = []
    scheduler_registry = SchedulerRegistry()
    scheduler_write = SchedulerWrite(scheduler_registry, SchedulerDriver(scheduler_registry, bus), bus)
    scheduler_clock = SchedulerClock()
    scheduler_clock_write = SchedulerClockWrite(scheduler_clock, bus)

    class _FakeRefresh:
        def refresh(self) -> list[object]:
            calls.append("refresh")
            return []

    class _FakeVisibilityRead:
        def __init__(self) -> None:
            self.visible = False

        def global_visible(self) -> bool:
            return self.visible

    visibility = _FakeVisibilityRead()
    policy = WidgetRefreshPolicy(
        records_refresh=cast(Any, _FakeRefresh()),
        visibility_read=cast(Any, visibility),
        scheduler_write=scheduler_write,
        scheduler_clock_read=SchedulerClockRead(scheduler_clock),
        events=bus,
    )

    policy.attach()
    scheduler_clock_write.request_clock_mode("tests", "live")
    scheduler_write.tick(0)
    bus.emit_typed(EventType.WIDGET_VISIBILITY_CHANGED, data=None, source="widgets")
    visibility.visible = True
    bus.emit_typed(EventType.WIDGET_VISIBILITY_CHANGED, data=None, source="widgets")
    scheduler_write.tick(20)

    assert calls == ["refresh", "refresh", "refresh"]


def test_widget_refresh_policy_refreshes_visibility_changes_without_live_clock() -> None:
    """Widget visibility changes should project immediately even before live ticks start."""

    bus = EventBus()
    calls: list[str] = []
    scheduler_registry = SchedulerRegistry()
    scheduler_write = SchedulerWrite(scheduler_registry, SchedulerDriver(scheduler_registry, bus), bus)
    scheduler_clock = SchedulerClock()

    class _FakeRefresh:
        def refresh(self) -> list[object]:
            calls.append("refresh")
            return []

    class _FakeVisibilityRead:
        def global_visible(self) -> bool:
            return True

    policy = WidgetRefreshPolicy(
        records_refresh=cast(Any, _FakeRefresh()),
        visibility_read=cast(Any, _FakeVisibilityRead()),
        scheduler_write=scheduler_write,
        scheduler_clock_read=SchedulerClockRead(scheduler_clock),
        events=bus,
    )

    policy.attach()
    bus.emit_typed(EventType.WIDGET_VISIBILITY_CHANGED, data=None, source="widgets")
    scheduler_write.tick(20)

    assert calls == ["refresh"]


def test_widget_refresh_policy_can_unsubscribe() -> None:
    """Widget refresh policy should remove its runtime event listeners on close."""

    bus = EventBus()
    calls: list[str] = []
    scheduler_registry = SchedulerRegistry()
    scheduler_write = SchedulerWrite(scheduler_registry, SchedulerDriver(scheduler_registry, bus), bus)
    scheduler_clock = SchedulerClock()
    scheduler_clock_write = SchedulerClockWrite(scheduler_clock, bus)

    class _FakeRefresh:
        def refresh(self) -> list[object]:
            calls.append("refresh")
            return []

    class _FakeVisibilityRead:
        def global_visible(self) -> bool:
            return True

    policy = WidgetRefreshPolicy(
        records_refresh=cast(Any, _FakeRefresh()),
        visibility_read=cast(Any, _FakeVisibilityRead()),
        scheduler_write=scheduler_write,
        scheduler_clock_read=SchedulerClockRead(scheduler_clock),
        events=bus,
    )

    policy.attach()
    policy.close()
    scheduler_clock_write.request_clock_mode("tests", "live")
    scheduler_write.tick(0)

    assert calls == []


def test_widget_records_refresh_marks_ready_when_connector_is_live_without_overlay_selection(tmp_path) -> None:
    """Widget refresh should make an overlay runtime-active when its connector is live."""

    overlay_id = "demo_overlay"
    connector_service = _FakeConnectorService([("car.speed", "321 km/h")], active_source="lmu")
    connector_services = ConnectorServiceRegistry()
    decision_store = ConnectorGameStateDecisionStore()
    decision_store.set("iracing", ConnectorGameStateDecision(show_widgets=True))
    connector_services.register(
        "iracing",
        "iracing",
        "IRacing",
        connector_service,
    )
    widget_config_store = WidgetConfigStore(_repository(tmp_path))
    WidgetConfigWrite(widget_config_store).set_global_widgets_visible(True)
    widget_config = WidgetConfigRead(widget_config_store)
    store = WidgetRecordsStore()
    refresh = _widget_records_refresh(
        store=store,
        overlay_read=_FakeOverlayRead(
            {
                overlay_id: OverlayManifest(
                    connectors=["iracing"],
                    widgets=[OverlayWidgetDecl(id="speed", widget="gauge", bindings={"source": "car.speed"})],
                )
            }
        ),
        connector_decl_read=_FakeConnectorDeclRead(
            {
                "iracing": ConnectorManifest(
                    service=ConnectorServiceDecl(module="plugins.iracing", class_name="IRacingService")
                )
            }
        ),
        connector_read=ConnectorRead(connector_services, decision_store),
        active_read=_FakeActiveRead(None),
        widget_config_read=widget_config,
        events=EventBus(),
    )

    record = refresh.refresh()[0]

    assert record.status == WidgetStatus.READY
    assert record.resolved_value == "321 km/h"


def test_widget_records_refresh_focus_hides_siblings_without_disabling_config(tmp_path) -> None:
    """Focused widget visibility should not mutate persisted enabled state."""

    overlay_id = "demo_overlay"
    connector_id = "iracing"
    store = WidgetRecordsStore()
    bus = EventBus()
    connector_services = ConnectorServiceRegistry()
    connector_services.register(
        connector_id,
        connector_id,
        "iRacing",
        _FakeConnectorService([("car.speed", "321 km/h"), ("car.rpm", "7200")]),
    )
    widget_store = WidgetConfigStore(_repository(tmp_path))
    WidgetConfigWrite(widget_store).set_global_widgets_visible(True)
    widget_config_read = WidgetConfigRead(widget_store)
    visibility_focus = WidgetVisibilityFocus()
    visibility_read = WidgetVisibilityRead(widget_config_read, visibility_focus)
    assert visibility_focus.focus_widget(overlay_id, "speed") is True
    refresh = _widget_records_refresh(
        store=store,
        overlay_read=_FakeOverlayRead(
            {
                overlay_id: OverlayManifest(
                    connectors=[connector_id],
                    widgets=[
                        OverlayWidgetDecl(
                            id="speed",
                            widget="text",
                            label="Speed",
                            bindings={"source": "car.speed"},
                        ),
                        OverlayWidgetDecl(
                            id="rpm",
                            widget="text",
                            label="RPM",
                            bindings={"source": "car.rpm"},
                        ),
                    ],
                )
            }
        ),
        connector_decl_read=_FakeConnectorDeclRead(
            {
                connector_id: ConnectorManifest(
                    service=ConnectorServiceDecl(module="plugins.iracing", class_name="IRacingService")
                )
            }
        ),
        connector_read=ConnectorRead(connector_services),
        active_read=_FakeActiveRead(None),
        widget_config_read=widget_config_read,
        events=bus,
        visibility_read=visibility_read,
    )

    records = {record.widget_id: record for record in refresh.refresh()}

    assert records["speed"].enabled is True
    assert records["speed"].status == WidgetStatus.READY
    assert records["rpm"].enabled is True
    assert records["rpm"].status == WidgetStatus.HIDDEN


def test_widget_visibility_capabilities_project_and_persist_visibility(tmp_path) -> None:
    """Widget visibility should stay widgets-owned while persisting through widget config."""

    store = WidgetConfigStore(_repository(tmp_path))
    from runtimeV2.widgets.capabilities.widget_manual_override import WidgetManualOverride
    config_write = WidgetConfigWrite(store)
    visibility_focus = WidgetVisibilityFocus()
    visibility_read = WidgetVisibilityRead(WidgetConfigRead(store), visibility_focus)
    bus = EventBus()
    manual_override = WidgetManualOverride()
    visibility_write = WidgetVisibilityWrite(config_write, manual_override, bus, visibility_focus)

    assert visibility_read.global_visible() is False
    visibility_write.set_global_visible(False)
    assert visibility_read.state().global_visible is False

    assert visibility_write.set_widget_enabled("demo_overlay", "speed", False) is True
    assert visibility_read.is_widget_enabled("demo_overlay", "speed") is False
    visibility_events = bus.get_history(EventType.WIDGET_VISIBILITY_CHANGED)
    assert len(visibility_events) == 2
    assert visibility_events[0].data == WidgetVisibilityChangedData(
        scope="global",
        global_visible=False,
    )
    assert visibility_events[1].data == WidgetVisibilityChangedData(
        scope="widget",
        global_visible=True,
        overlay_id="demo_overlay",
        widget_id="speed",
        enabled=False,
    )

    assert visibility_write.focus_widget("demo_overlay", "speed") is True
    assert visibility_read.focused_widget() == ("demo_overlay", "speed")
    assert visibility_write.clear_focus() is True
    assert visibility_read.focused_widget() is None
