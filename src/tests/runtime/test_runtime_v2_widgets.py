"""Tests for runtime V2 widgets."""

from __future__ import annotations

from runtimeV2.connectors.capabilities.connector_read import ConnectorRead
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
    connector_services.register("iracing", "iracing", "IRacing", object())
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
