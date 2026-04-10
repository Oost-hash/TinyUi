"""Tests for runtime V2 widgets."""

from __future__ import annotations

from runtimeV2.persistence.capabilities.widget_config_write import WidgetConfigWrite
from runtimeV2.connectors.capabilities.connector_read import ConnectorRead
from runtimeV2.connectors.contracts import ConnectorGameStateDecision
from runtimeV2.connectors.decision_store import ConnectorGameStateDecisionStore
from runtimeV2.connectors.service_registry import ConnectorServiceRegistry
from runtimeV2.events.contracts import EventBus, EventType
from runtimeV2.manifest.capabilities.connector_read import ManifestConnectorRead
from runtimeV2.manifest.capabilities.overlay_read import ManifestOverlayRead
from runtimeV2.connectors.schemas.manifest import ConnectorManifest
from runtimeV2.connectors.schemas.manifest import ConnectorServiceDecl
from runtimeV2.persistence.capabilities.widget_config_read import WidgetConfigRead
from runtimeV2.persistence.contracts import PersistencePaths
from runtimeV2.persistence.widget_config import WidgetConfigStore
from runtimeV2.plugins.capabilities.active_read import PluginActiveRead
from runtimeV2.widgets.capabilities.widget_records_read import WidgetRecordsRead
from runtimeV2.widgets.capabilities.widget_records_refresh import WidgetRecordsRefresh
from runtimeV2.widgets.capabilities.widget_visibility_read import WidgetVisibilityRead
from runtimeV2.widgets.capabilities.widget_visibility_write import WidgetVisibilityWrite
from runtimeV2.widgets.contracts import WidgetVisibilityChangedData
from runtimeV2.widgets.poller import WidgetRuntimePoller
from runtimeV2.widgets.store import WidgetRecordsStore
from runtimeV2.widgets.schemas.manifest import OverlayManifest, OverlayWidgetDecl, WidgetDefaults
from runtimeV2.widgets.contracts import WidgetStatus


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
    base_dir = tmp_path / "TinyUi"
    config_root = base_dir / "config"
    paths = PersistencePaths(
        base_dir=base_dir,
        config_root=config_root,
        cache_dir=base_dir / "cache",
        logs_dir=base_dir / "logs",
        bootstrap_path=base_dir / "bootstrap.toml",
        config_sets_path=config_root / "config_sets.json",
    )
    store = WidgetConfigStore(paths, "default")
    store.set_widget_enabled(overlay_id, widget_id, False)
    store.set_widget_position(overlay_id, widget_id, 12, 34)
    store.set_widget_values(overlay_id, widget_id, {"units": "kph"})
    return WidgetConfigRead(store)


def test_widget_runtime_poller_merges_config_and_emits_update(tmp_path) -> None:
    """Widget refresh should merge widget config into widget runtime records."""

    overlay_id = "demo_overlay"
    widget_id = "speed"
    store = WidgetRecordsStore()
    bus = EventBus()
    poller = WidgetRuntimePoller(
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

    records = poller.refresh()

    assert len(records) == 1
    record = records[0]
    assert record.bindings == {"source": "car.speed"}
    assert record.enabled is False
    assert record.position == (12, 34)
    assert record.values == {"units": "kph"}
    assert record.status == WidgetStatus.HIDDEN
    assert store.widget_record(overlay_id, widget_id) == record
    assert bus.get_history()[-1].type == EventType.WIDGET_RUNTIME_UPDATED


def test_widget_runtime_poller_marks_ready_when_active_and_connected(tmp_path) -> None:
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
    base_dir = tmp_path / "TinyUi"
    config_root = base_dir / "config"
    widget_config = WidgetConfigRead(
        WidgetConfigStore(
            PersistencePaths(
                base_dir=base_dir,
                config_root=config_root,
                cache_dir=base_dir / "cache",
                logs_dir=base_dir / "logs",
                bootstrap_path=base_dir / "bootstrap.toml",
                config_sets_path=config_root / "config_sets.json",
            ),
            "default",
        )
    )
    store = WidgetRecordsStore()
    poller = WidgetRuntimePoller(
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

    record = poller.refresh()[0]

    assert record.status == WidgetStatus.READY
    assert record.enabled is True
    assert record.position == (0, 0)
    assert record.resolved_value == "321 km/h"


def test_widget_records_read_exposes_store_projection(tmp_path) -> None:
    """Widget records read should expose the store without adding extra policy."""

    overlay_id = "demo_overlay"
    widget_id = "speed"
    store = WidgetRecordsStore()
    poller = WidgetRuntimePoller(
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

    poller.refresh()
    read = WidgetRecordsRead(store)
    record = read.widget_record(overlay_id, widget_id)

    assert record is not None
    assert read.records_for_overlay(overlay_id) == [record]
    assert read.all_widget_records() == [record]


def test_widget_records_refresh_uses_widget_runtime_poller(tmp_path) -> None:
    """Widget refresh capability should delegate to the widgets-owned poller."""

    overlay_id = "demo_overlay"
    widget_id = "speed"
    store = WidgetRecordsStore()
    poller = WidgetRuntimePoller(
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
    refresh = WidgetRecordsRefresh(poller)

    records = refresh.refresh()

    assert records == store.all_widget_records()
    assert len(records) == 1


def test_widget_runtime_poller_marks_ready_when_connector_is_live_without_overlay_selection(tmp_path) -> None:
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
    base_dir = tmp_path / "TinyUi"
    config_root = base_dir / "config"
    widget_config = WidgetConfigRead(
        WidgetConfigStore(
            PersistencePaths(
                base_dir=base_dir,
                config_root=config_root,
                cache_dir=base_dir / "cache",
                logs_dir=base_dir / "logs",
                bootstrap_path=base_dir / "bootstrap.toml",
                config_sets_path=config_root / "config_sets.json",
            ),
            "default",
        )
    )
    store = WidgetRecordsStore()
    poller = WidgetRuntimePoller(
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

    record = poller.refresh()[0]

    assert record.status == WidgetStatus.READY
    assert record.resolved_value == "321 km/h"


def test_widget_visibility_capabilities_project_and_persist_visibility(tmp_path) -> None:
    """Widget visibility should stay widgets-owned while persisting through widget config."""

    base_dir = tmp_path / "TinyUi"
    config_root = base_dir / "config"
    store = WidgetConfigStore(
        PersistencePaths(
            base_dir=base_dir,
            config_root=config_root,
            cache_dir=base_dir / "cache",
            logs_dir=base_dir / "logs",
            bootstrap_path=base_dir / "bootstrap.toml",
            config_sets_path=config_root / "config_sets.json",
        ),
        "default",
    )
    config_write = WidgetConfigWrite(store)
    visibility_read = WidgetVisibilityRead(WidgetConfigRead(store))
    bus = EventBus()
    visibility_write = WidgetVisibilityWrite(config_write, bus)

    assert visibility_read.global_visible() is True
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
