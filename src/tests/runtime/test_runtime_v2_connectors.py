#  TinyUI
#  Copyright (C) 2026 Oost-hash
#
#  This file is part of TinyUI.
#
#  TinyUI is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  TinyUI is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#  TinyUI builds on TinyPedal by s-victor (https://github.com/s-victor/TinyPedal),
#  licensed under GPLv3.

"""Tests for runtime V2 connectors."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Any, cast

from plugins.LMU_RF2_Connector import plugin as lmu_rf2_plugin
from plugins.LMU_RF2_Connector.service import LMURF2ConnectorService
from runtimeV2.capabilities.runtime_globals import RuntimeGlobals
from runtimeV2.connectors.capabilities.connector_read import ConnectorRead
from runtimeV2.connectors.capabilities.connector_write import ConnectorWrite
from runtimeV2.contracts import (
    ConnectorGameDetectedData,
    ConnectorGameLostData,
    ConnectorSourceChangedData,
)
from runtimeV2.connectors.policy import unregister_connector_service
from runtimeV2.connectors.schemas.manifest import (
    ConnectorGameDecl,
    ConnectorManifest,
    ConnectorRuntimeDecl,
    ConnectorServiceDecl,
)
from runtimeV2.manifest.parser import load_plugin_manifest
from runtimeV2.scheduler.capabilities.scheduler_write import SchedulerWrite
from runtimeV2.scheduler.capabilities.scheduler_read import SchedulerRead
from runtimeV2.scheduler.capabilities.scheduler_clock_read import SchedulerClockRead
from runtimeV2.scheduler.capabilities.scheduler_clock_write import SchedulerClockWrite
from runtimeV2.scheduler.clock import SchedulerClock
from runtimeV2.scheduler.driver import SchedulerDriver
from runtimeV2.scheduler.registry import SchedulerRegistry
from runtimeV2.connectors.startup_shutdown.startup import startup_connectors, ConnectorsStartupResult
from runtimeV2.contracts import EventBus, EventType
from runtimeV2.events.event_registry import EventRegistry
from runtimeV2.events.startup_shutdown.startup import EventsStartupResult
from runtimeV2.globals import GlobalRegistration
from runtimeV2.manifest.capabilities.connector_read import ManifestConnectorRead
from runtimeV2.persistence.capabilities.widget_config_write import WidgetConfigWrite
from runtimeV2.schemas.startup import StartupResult
from runtimeV2.widgets.capabilities.widget_manual_override import WidgetManualOverride
from runtimeV2.widgets.capabilities.widget_visibility_write import WidgetVisibilityWrite


class _FakeConnectorService:
    def __init__(self) -> None:
        self.open_called = False
        self.update_calls = 0
        self.requested: list[tuple[str, str]] = []
        self.released: list[str] = []
        self.closed = False
        self.state = _FakeState(False)
        self._game_phase: int | None = 0
        self._has_player_vehicle: bool | None = False
        self._in_realtime: bool | None = False

    def supports_source(self, source_name: str) -> bool:
        return source_name == "mock"

    def request_source(self, owner: str, source_name: str) -> bool:
        self.requested.append((owner, source_name))
        return True

    def open(self) -> None:
        self.open_called = True

    def update(self) -> None:
        self.update_calls += 1

    def inspect_snapshot(self) -> list[tuple[str, str]]:
        return [("speed", "321")]

    def active_source(self) -> str:
        return "mock"

    def active_game(self) -> str:
        return "mock"

    def game_phase(self) -> int | None:
        return self._game_phase

    def has_player_vehicle(self) -> bool | None:
        return self._has_player_vehicle

    def in_realtime(self) -> bool | None:
        return self._in_realtime

    def release_source(self, owner: str) -> bool:
        self.released.append(owner)
        return True

    def close(self) -> None:
        self.closed = True


class _FakeLiveConnectorService(_FakeConnectorService):
    def __init__(self) -> None:
        super().__init__()
        self._active_source = "mock"
        self._active_game = "mock"

    def update(self) -> None:
        super().update()
        self._active_source = "lmu"
        self._active_game = "lmu"
        self.state = _FakeState(True)
        self._game_phase = 5
        self._has_player_vehicle = True
        self._in_realtime = True

    def active_source(self) -> str:
        return self._active_source

    def active_game(self) -> str:
        return self._active_game


class _FakeStickyLiveConnectorService(_FakeConnectorService):
    def __init__(self) -> None:
        super().__init__()
        self._active_source = "lmu"
        self._active_game = "lmu"
        self._game_phase = 5
        self._has_player_vehicle = True
        self._in_realtime = True
        self.state = _FakeState(True)

    def update(self) -> None:
        super().update()
        if self.update_calls == 1:
            self._game_phase = 5
            self._has_player_vehicle = True
            self._in_realtime = True
            self.state = _FakeState(True)
            return
        self._game_phase = 9
        self._has_player_vehicle = True
        self._in_realtime = False
        self.state = _FakeState(True)

    def active_source(self) -> str:
        return self._active_source

    def active_game(self) -> str:
        return self._active_game


class _FakeExitLiveConnectorService(_FakeConnectorService):
    def __init__(self) -> None:
        super().__init__()
        self._active_source = "lmu"
        self._active_game = "lmu"
        self._game_phase = 5
        self._has_player_vehicle = True
        self._in_realtime = True
        self.state = _FakeState(True)

    def update(self) -> None:
        super().update()
        self._active_source = "lmu"
        self._active_game = "lmu"
        self._game_phase = 5
        self._has_player_vehicle = True
        self._in_realtime = True
        self.state = _FakeState(True)

    def active_source(self) -> str:
        return self._active_source

    def active_game(self) -> str:
        return self._active_game


class _FakeState:
    def __init__(self, active: bool) -> None:
        self._active = active

    def active(self) -> bool:
        return self._active

    def paused(self) -> bool:
        return False

    def version(self) -> str:
        return "test"


class _FakeReader:
    def __init__(self, active: bool) -> None:
        self.state = _FakeState(active)


class _FakeSource:
    def __init__(self, name: str, *, kind: str, game: str, active: bool) -> None:
        self.name = name
        self.kind = kind
        self.game = game
        self.description = f"{name} source"
        self.reader = _FakeReader(active)
        self.open_calls = 0
        self.close_calls = 0
        self.update_calls = 0

    def open(self) -> None:
        self.open_calls += 1

    def close(self) -> None:
        self.close_calls += 1

    def update(self) -> None:
        self.update_calls += 1


class _FakeManifestConnectorRead:
    def __init__(self, declarations: dict[str, ConnectorManifest]) -> None:
        self._declarations = declarations

    def connector_declarations(self) -> dict[str, ConnectorManifest]:
        return dict(self._declarations)


@dataclass(frozen=True)
class _FakeRuntime:
    _domain_results: dict[str, object]
    _capabilities: dict[str, object]
    registered_capabilities: dict[str, object]
    registered_results: dict[str, object]
    registered_globals: dict[str, GlobalRegistration]

    def domain_result(self, name: str, _result_type: type[Any]) -> Any:
        return self._domain_results[name]

    def capability(self, name: str, _capability_type: type[Any]) -> Any:
        if name in self.registered_capabilities:
            return self.registered_capabilities[name]
        return self._capabilities[name]

    def try_capability(self, name: str) -> object | None:
        if name in self.registered_capabilities:
            return self.registered_capabilities[name]
        return self._capabilities.get(name)

    def register_capability(self, name: str, capability: object) -> None:
        self.registered_capabilities[name] = capability

    def register_domain_result(self, name: str, result: object) -> None:
        self.registered_results[name] = result

    def register_global(
        self,
        name: str,
        *,
        owner_domain: str,
        description: str = "",
        read_capability: str = "",
        write_capability: str = "",
        event_type=None,
    ) -> None:
        self.registered_globals[name] = GlobalRegistration(
            name=name,
            owner_domain=owner_domain,
            description=description,
            read_capability=read_capability,
            write_capability=write_capability,
            event_type=event_type,
        )

    def global_record(self, name: str) -> GlobalRegistration:
        return self.registered_globals[name]


def _make_runtime(declarations: dict[str, ConnectorManifest]) -> tuple[_FakeRuntime, EventBus]:
    bus = EventBus()
    events = EventsStartupResult(
        bus=bus,
        registry=EventRegistry(),
        event_read=cast(Any, object()),
    )
    registered_capabilities: dict[str, object] = {}
    runtime = _FakeRuntime(
        _domain_results={"events": events},
        _capabilities={
            "manifest_connector_read": _FakeManifestConnectorRead(declarations),
            "settings_read": cast(Any, _FakeSettingsRead()),
            "widget_config_write": cast(Any, _FakeWidgetConfigWrite()),
        },
        registered_capabilities=registered_capabilities,
        registered_results={},
        registered_globals={},
    )
    registered_capabilities["globals"] = RuntimeGlobals(cast(Any, runtime))
    scheduler_registry = SchedulerRegistry()
    scheduler_driver = SchedulerDriver(scheduler_registry, bus)
    scheduler_clock = SchedulerClock()
    registered_capabilities["scheduler_write"] = SchedulerWrite(scheduler_registry, scheduler_driver, bus)
    registered_capabilities["scheduler_read"] = SchedulerRead(scheduler_registry)
    registered_capabilities["scheduler_clock_write"] = SchedulerClockWrite(scheduler_clock, bus)
    registered_capabilities["scheduler_clock_read"] = SchedulerClockRead(scheduler_clock)
    # Register widget visibility capabilities for connector handoff tests
    fake_widget_config_write = cast(WidgetConfigWrite, runtime._capabilities["widget_config_write"])
    manual_override = WidgetManualOverride()
    registered_capabilities["widget_manual_override"] = manual_override
    registered_capabilities["widget_visibility_write"] = WidgetVisibilityWrite(
        fake_widget_config_write, manual_override, bus
    )
    return runtime, bus


class _FakeSettingsRead:
    def get(self, namespace: str, key: str) -> int | None:
        if namespace == "tinyui" and key == "connector_poll_interval_ms":
            return 20
        return None


class _FakeWidgetConfigWrite:
    def __init__(self) -> None:
        self.global_visible = True
        self.calls: list[bool] = []

    def set_global_widgets_visible(self, visible: bool) -> None:
        self.global_visible = visible
        self.calls.append(visible)


def _connector_manifest(
    module_name: str,
    class_name: str = "IRacingService",
    *,
    game_id: str = "iracing",
    detect_names: list[str] | None = None,
    runtime: ConnectorRuntimeDecl | None = None,
) -> ConnectorManifest:
    return ConnectorManifest(
        games=[ConnectorGameDecl(id=game_id, detect_names=detect_names or ["iRacing"])],
        service=ConnectorServiceDecl(module=module_name, class_name=class_name),
        runtime=runtime,
    )


def test_startup_connectors_registers_declared_services(monkeypatch) -> None:
    """Connectors startup should load and register manifest-declared services."""

    service = _FakeConnectorService()
    monkeypatch.setattr(
        "runtimeV2.connectors.policy.load_connector_service",
        lambda module_name, class_name: service,
    )
    monkeypatch.setattr(
        "runtimeV2.connectors.game_detector.psutil.process_iter",
        lambda attrs=None: [type("Proc", (), {"info": {"name": "iRacing"}})()],
    )

    runtime, bus = _make_runtime(
        {
            "iracing": _connector_manifest("plugins.iracing")
        }
    )

    result = startup_connectors(cast(Any, runtime))

    assert result == StartupResult(ok=True)
    startup_result = cast(ConnectorsStartupResult, runtime.registered_results["connectors"])
    assert startup_result.registry.has("iracing") is True
    assert startup_result.capabilities.read.ids() == ["iracing"]
    assert startup_result.capabilities.read.inspection_rows("iracing") == [("speed", "321")]
    assert startup_result.capabilities.read.inspection_map("iracing") == {"speed": "321"}
    assert startup_result.capabilities.read.value("iracing", "speed") == "321"
    assert service.open_called is True
    assert service.update_calls == 0
    assert service.requested == []
    scheduler_write = cast(SchedulerWrite, runtime.registered_capabilities["scheduler_write"])
    scheduler_write.tick(5000)
    assert service.update_calls == 1
    scheduler_write.tick(5020)
    assert service.update_calls == 1
    scheduler_write.tick(10000)
    assert service.update_calls == 2
    scheduler_jobs = cast(SchedulerRead, runtime.registered_capabilities["scheduler_read"]).jobs()
    assert [job.job_id for job in scheduler_jobs] == [
        "connectors.iracing.probe_game_state",
        "connectors.iracing.live_poll",
    ]
    assert scheduler_jobs[0].enabled is True
    assert scheduler_jobs[1].enabled is False
    # Check key events are present.
    event_types = [event.type for event in bus.get_history()]
    assert EventType.CONNECTOR_SERVICE_REGISTERED in event_types
    assert EventType.CONNECTOR_GAME_DETECTED in event_types
    assert EventType.SCHEDULER_TICK in event_types


def test_connector_write_can_update_all_services(monkeypatch) -> None:
    """Connector write capability should update all active services."""

    services = {
        "iracing": _FakeConnectorService(),
        "acc": _FakeConnectorService(),
    }

    def _load_service(module_name: str, class_name: str) -> _FakeConnectorService:
        return services[module_name]

    monkeypatch.setattr("runtimeV2.connectors.policy.load_connector_service", _load_service)
    monkeypatch.setattr(
        "runtimeV2.connectors.game_detector.psutil.process_iter",
        lambda attrs=None: [type("Proc", (), {"info": {"name": "iRacing"}})(), type("Proc", (), {"info": {"name": "Assetto Corsa Competizione"}})()],
    )

    runtime, bus = _make_runtime(
        {
            "iracing": _connector_manifest("iracing", "Service", game_id="iracing", detect_names=["iRacing"]),
            "acc": _connector_manifest("acc", "Service", game_id="acc", detect_names=["Assetto Corsa Competizione"]),
        }
    )

    assert startup_connectors(cast(Any, runtime)) == StartupResult(ok=True)
    write = cast(ConnectorWrite, runtime.registered_capabilities["connector_write"])
    read = cast(ConnectorRead, runtime.registered_capabilities["connector_read"])

    updated = write.update_all()

    assert updated == ["iracing", "acc"]
    assert services["iracing"].update_calls == 1
    assert services["acc"].update_calls == 1
    assert read.service("iracing") is not None
    assert len(bus.get_history(EventType.CONNECTOR_SERVICE_UPDATED)) == 4


def test_connector_scheduler_switches_from_probe_to_live_mode(monkeypatch) -> None:
    """Connectors should enable live polling after probe detects a real source."""

    service = _FakeLiveConnectorService()
    monkeypatch.setattr(
        "runtimeV2.connectors.policy.load_connector_service",
        lambda module_name, class_name: service,
    )
    monkeypatch.setattr(
        "runtimeV2.connectors.game_detector.psutil.process_iter",
        lambda attrs=None: [type("Proc", (), {"info": {"name": "iRacing"}})()],
    )
    runtime, _bus = _make_runtime(
        {
            "iracing": _connector_manifest("plugins.iracing")
        }
    )

    assert startup_connectors(cast(Any, runtime)) == StartupResult(ok=True)

    scheduler_write = cast(SchedulerWrite, runtime.registered_capabilities["scheduler_write"])
    scheduler_read = cast(SchedulerRead, runtime.registered_capabilities["scheduler_read"])

    scheduler_write.tick(5000)

    jobs = {job.job_id: job for job in scheduler_read.jobs()}
    assert jobs["connectors.iracing.probe_game_state"].enabled is False
    assert jobs["connectors.iracing.live_poll"].enabled is True
    assert service.active_source() == "lmu"
    assert service.update_calls == 1

    scheduler_write.tick(5020)
    assert service.update_calls == 2


def test_connector_write_emits_source_change_events(monkeypatch) -> None:
    """Connector source requests should emit events and drive mock preview cadence."""

    service = _FakeConnectorService()
    monkeypatch.setattr(
        "runtimeV2.connectors.policy.load_connector_service",
        lambda module_name, class_name: service,
    )
    monkeypatch.setattr(
        "runtimeV2.connectors.game_detector.psutil.process_iter",
        lambda attrs=None: [type("Proc", (), {"info": {"name": "iRacing"}})()],
    )
    runtime, bus = _make_runtime(
        {
            "iracing": _connector_manifest("plugins.iracing")
        }
    )

    assert startup_connectors(cast(Any, runtime)) == StartupResult(ok=True)
    write = cast(ConnectorWrite, runtime.registered_capabilities["connector_write"])
    scheduler_read = cast(SchedulerRead, runtime.registered_capabilities["scheduler_read"])
    scheduler_clock_read = cast(SchedulerClockRead, runtime.registered_capabilities["scheduler_clock_read"])

    assert write.request_source("iracing", "devtools", "mock") is True
    jobs = {job.job_id: job for job in scheduler_read.jobs()}
    assert jobs["connectors.iracing.probe_game_state"].enabled is False
    assert jobs["connectors.iracing.live_poll"].enabled is True
    assert scheduler_clock_read.clock_mode() == "live"
    assert scheduler_clock_read.clock_interval_ms() == 20
    assert scheduler_clock_read.clock_locked_by() is None

    assert write.release_source("iracing", "devtools") is True
    jobs = {job.job_id: job for job in scheduler_read.jobs()}
    assert jobs["connectors.iracing.probe_game_state"].enabled is True
    assert jobs["connectors.iracing.live_poll"].enabled is False
    assert scheduler_clock_read.clock_mode() == "idle"

    history = bus.get_history(EventType.CONNECTOR_SOURCE_CHANGED)
    assert [event.data for event in history] == [
        ConnectorSourceChangedData(
            connector_id="iracing",
            plugin_id="iracing",
            owner="devtools",
            source_name="mock",
            action="request",
        ),
        ConnectorSourceChangedData(
            connector_id="iracing",
            plugin_id="iracing",
            owner="devtools",
            source_name="",
            action="release",
        ),
    ]


def test_mock_source_keeps_live_polling_without_detected_game(monkeypatch) -> None:
    """Mock preview should keep the connector live job running without a detected game."""

    service = _FakeConnectorService()
    monkeypatch.setattr(
        "runtimeV2.connectors.policy.load_connector_service",
        lambda module_name, class_name: service,
    )
    monkeypatch.setattr(
        "runtimeV2.connectors.game_detector.psutil.process_iter",
        lambda attrs=None: [],
    )
    runtime, _bus = _make_runtime(
        {
            "iracing": _connector_manifest("plugins.iracing")
        }
    )

    assert startup_connectors(cast(Any, runtime)) == StartupResult(ok=True)
    write = cast(ConnectorWrite, runtime.registered_capabilities["connector_write"])
    scheduler_write = cast(SchedulerWrite, runtime.registered_capabilities["scheduler_write"])
    scheduler_read = cast(SchedulerRead, runtime.registered_capabilities["scheduler_read"])
    scheduler_clock_read = cast(SchedulerClockRead, runtime.registered_capabilities["scheduler_clock_read"])

    assert write.request_source("iracing", "devtools", "mock") is True
    scheduler_write.tick(0)
    scheduler_write.tick(20)

    jobs = {job.job_id: job for job in scheduler_read.jobs()}
    assert jobs["connectors.iracing.probe_game_state"].enabled is False
    assert jobs["connectors.iracing.live_poll"].enabled is True
    assert scheduler_clock_read.clock_mode() == "live"
    assert scheduler_clock_read.clock_locked_by() is None
    assert service.update_calls == 2


def test_unregister_connector_service_releases_source_and_closes(monkeypatch) -> None:
    """Connector unregister should release runtime mock source and close the service."""

    service = _FakeConnectorService()
    monkeypatch.setattr(
        "runtimeV2.connectors.policy.load_connector_service",
        lambda module_name, class_name: service,
    )
    monkeypatch.setattr(
        "runtimeV2.connectors.game_detector.psutil.process_iter",
        lambda attrs=None: [type("Proc", (), {"info": {"name": "iRacing"}})()],
    )
    runtime, bus = _make_runtime(
        {
            "iracing": _connector_manifest("plugins.iracing")
        }
    )
    assert startup_connectors(cast(Any, runtime)) == StartupResult(ok=True)
    startup_result = cast(ConnectorsStartupResult, runtime.registered_results["connectors"])

    removed = unregister_connector_service(
        connector_id="iracing",
        connector_services=startup_result.registry,
        events=bus,
    )

    assert removed is True
    assert service.released == ["__runtime__"]
    assert service.closed is True
    assert startup_result.registry.has("iracing") is False
    assert bus.get_history()[-1].type == EventType.CONNECTOR_SERVICE_UNREGISTERED


def test_connector_service_prefers_active_real_source_over_mock() -> None:
    """Connector family service should switch to a live source when it reports active state."""

    lmu = _FakeSource("lmu", kind="shared-memory", game="lmu", active=True)
    rf2 = _FakeSource("rf2", kind="shared-memory", game="rf2", active=False)

    runtime = LMURF2ConnectorService(cast(Any, lmu), cast(Any, rf2))

    runtime.open()
    runtime.update()

    assert runtime.active_source() == "lmu"
    assert runtime.active_game() == "lmu"


def test_connector_service_falls_back_to_mock_without_active_real_source() -> None:
    """Connector family service should keep mock active when no live source reports activity."""

    lmu = _FakeSource("lmu", kind="shared-memory", game="lmu", active=False)
    rf2 = _FakeSource("rf2", kind="shared-memory", game="rf2", active=False)

    runtime = LMURF2ConnectorService(cast(Any, lmu), cast(Any, rf2))

    runtime.open()
    runtime.update()

    assert runtime.active_source() == "mock"
    assert runtime.active_game() == "mock"


def test_connector_manifest_parses_runtime_handoff_metadata(tmp_path: Path) -> None:
    """Connector manifests should parse connector_runtime handoff metadata."""

    manifest_path = tmp_path / "manifest.toml"
    manifest_path.write_text(
        "\n".join([
            "[plugin]",
            'id = "LMU_RF2_Connector"',
            'type = "connector"',
            "",
            "[connector_service]",
            'module = "plugins.LMU_RF2_Connector.plugin"',
            'class = "LMURF2Connector"',
            "",
            "[connector_runtime]",
            'game_state_hook = "update_game_state"',
            'mock_source = "mock"',
            "",
        ]),
        encoding="utf-8",
    )

    manifest = load_plugin_manifest(manifest_path)

    assert manifest.connector is not None
    assert manifest.connector.runtime == ConnectorRuntimeDecl(game_state_hook="update_game_state", mock_source="mock")


def test_connector_scheduler_dispatches_manifest_declared_game_state_hook(monkeypatch) -> None:
    """Connectors should dispatch game-state changes into the declared plugin.py hook."""

    service = _FakeLiveConnectorService()
    updates: list[tuple[str, str, bool, bool, bool]] = []
    module = ModuleType("plugins.iracing.plugin")

    def update_game_state(update) -> object:
        updates.append((
            update.active_source,
            update.active_game,
            update.is_live,
            update.state_active,
            update.state_paused,
        ))
        return {"show_widgets": update.state_active and not update.state_paused}

    setattr(module, "update_game_state", update_game_state)

    monkeypatch.setattr(
        "runtimeV2.connectors.policy.load_connector_service",
        lambda module_name, class_name: service,
    )
    monkeypatch.setattr(
        "runtimeV2.connectors.plugin_handoff.importlib.import_module",
        lambda name: module,
    )
    monkeypatch.setattr(
        "runtimeV2.connectors.game_detector.psutil.process_iter",
        lambda attrs=None: [type("Proc", (), {"info": {"name": "iRacing"}})()],
    )

    runtime, _bus = _make_runtime(
        {
            "iracing": _connector_manifest(
                "plugins.iracing",
                runtime=ConnectorRuntimeDecl(game_state_hook="update_game_state"),
            )
        }
    )

    assert startup_connectors(cast(Any, runtime)) == StartupResult(ok=True)

    scheduler_write = cast(SchedulerWrite, runtime.registered_capabilities["scheduler_write"])

    assert updates == [("mock", "mock", False, False, False)]
    read = cast(ConnectorRead, runtime.registered_capabilities["connector_read"])
    # Mock source now forces show_widgets=True regardless of hook return value
    assert read.show_widgets("iracing") is True
    widget_config_write = cast(_FakeWidgetConfigWrite, runtime._capabilities["widget_config_write"])
    # Widget visibility is True because mock source forces it
    assert widget_config_write.global_visible is True

    scheduler_write.tick(5000)

    assert updates[-1] == ("lmu", "lmu", True, True, False)
    assert read.show_widgets("iracing") is True
    assert widget_config_write.global_visible is True
    # Two calls: first from mock source override (True), then from live game (True again)
    assert widget_config_write.calls == [True, True]


def test_startup_connectors_fails_without_detect_names(monkeypatch) -> None:
    """Connectors startup should fail hard when a family omits detect_names."""

    monkeypatch.setattr(
        "runtimeV2.connectors.policy.load_connector_service",
        lambda module_name, class_name: _FakeConnectorService(),
    )

    runtime, _bus = _make_runtime(
        {
            "iracing": ConnectorManifest(
                games=[ConnectorGameDecl(id="iracing", detect_names=[])],
                service=ConnectorServiceDecl(module="plugins.iracing", class_name="IRacingService"),
            )
        }
    )

    result = startup_connectors(cast(Any, runtime))

    assert result.ok is False
    assert "detect_names" in result.error_message


def test_connector_game_detector_emits_detected_and_lost_events(monkeypatch) -> None:
    """Connector game detection should emit explicit events when runtime state changes."""

    service = _FakeConnectorService()
    monkeypatch.setattr(
        "runtimeV2.connectors.policy.load_connector_service",
        lambda module_name, class_name: service,
    )
    process_names = [
        [type("Proc", (), {"info": {"name": "iRacing"}})()],
        [],
    ]
    monkeypatch.setattr(
        "runtimeV2.connectors.game_detector.psutil.process_iter",
        lambda attrs=None: process_names.pop(0),
    )
    runtime, bus = _make_runtime({"iracing": _connector_manifest("plugins.iracing")})

    assert startup_connectors(cast(Any, runtime)) == StartupResult(ok=True)
    game_detector_write = cast(Any, runtime.registered_capabilities["connector_game_detector_write"])
    read = cast(ConnectorRead, runtime.registered_capabilities["connector_read"])

    assert game_detector_write.sync("iracing") is not None
    assert read.detected_game("iracing") == "iracing"
    assert read.detected_process_name("iracing") == "iRacing"

    assert game_detector_write.sync("iracing") is None
    assert read.detected_game("iracing") is None

    game_events = [event.data for event in bus.get_history() if event.type in {EventType.CONNECTOR_GAME_DETECTED, EventType.CONNECTOR_GAME_LOST}]
    assert game_events == [
        ConnectorGameDetectedData(
            connector_id="iracing",
            plugin_id="iracing",
            game_id="iracing",
            process_name="iRacing",
        ),
        ConnectorGameLostData(
            connector_id="iracing",
            plugin_id="iracing",
            game_id="iracing",
            process_name="iRacing",
        ),
    ]


def test_connector_game_detector_matches_normalized_process_names(monkeypatch) -> None:
    """Connector game detection should match practical executable name variants."""

    monkeypatch.setattr(
        "runtimeV2.connectors.policy.load_connector_service",
        lambda module_name, class_name: _FakeConnectorService(),
    )
    monkeypatch.setattr(
        "runtimeV2.connectors.game_detector.psutil.process_iter",
        lambda attrs=None: [type("Proc", (), {"info": {"name": "LeMansUltimate.exe"}})()],
    )
    runtime, _bus = _make_runtime(
        {
            "LMU_RF2_Connector": ConnectorManifest(
                games=[
                    ConnectorGameDecl(id="lmu", detect_names=["Le Mans Ultimate"]),
                    ConnectorGameDecl(id="rf2", detect_names=["rFactor2", "rFactor2 Dedicated"]),
                ],
                service=ConnectorServiceDecl(
                    module="plugins.LMU_RF2_Connector.plugin",
                    class_name="LMURF2Connector",
                ),
            )
        }
    )

    assert startup_connectors(cast(Any, runtime)) == StartupResult(ok=True)
    read = cast(ConnectorRead, runtime.registered_capabilities["connector_read"])
    game_detector_write = cast(Any, runtime.registered_capabilities["connector_game_detector_write"])

    detected = game_detector_write.sync("LMU_RF2_Connector")

    assert detected is not None
    assert read.detected_game("LMU_RF2_Connector") == "lmu"
    assert read.detected_process_name("LMU_RF2_Connector") == "LeMansUltimate.exe"


def test_lmu_rf2_plugin_game_state_hook_accepts_both_live_games() -> None:
    """The LMU/RF2 connector plugin should enable widgets for both supported live games."""

    service = _FakeLiveConnectorService()
    lmu_rf2_plugin._service_instance = cast(Any, service)
    service._active_source = "lmu"
    service._active_game = "lmu"
    service._game_phase = 5
    service._has_player_vehicle = True
    service._in_realtime = True
    service.state = _FakeState(True)
    lmu_decision = lmu_rf2_plugin.update_game_state(
        cast(Any, type("Update", (), {
            "active_source": "lmu",
            "active_game": "lmu",
            "is_live": True,
            "state_active": True,
            "state_paused": False,
        })())
    )
    service._active_source = "rf2"
    service._active_game = "rf2"
    service.state = _FakeState(True)
    rf2_decision = lmu_rf2_plugin.update_game_state(
        cast(Any, type("Update", (), {
            "active_source": "rf2",
            "active_game": "rf2",
            "is_live": True,
            "state_active": True,
            "state_paused": False,
        })())
    )
    service._active_source = "mock"
    service._active_game = "mock"
    service._game_phase = 0
    service._has_player_vehicle = False
    service._in_realtime = False
    service.state = _FakeState(False)
    mock_decision = lmu_rf2_plugin.update_game_state(
        cast(Any, type("Update", (), {
            "active_source": "mock",
            "active_game": "mock",
            "is_live": False,
            "state_active": False,
            "state_paused": False,
        })())
    )
    service._active_source = "lmu"
    service._active_game = "lmu"
    service._in_realtime = True
    service.state = _FakeState(False)
    inactive_decision = lmu_rf2_plugin.update_game_state(
        cast(Any, type("Update", (), {
            "active_source": "lmu",
            "active_game": "lmu",
            "is_live": True,
            "state_active": False,
            "state_paused": False,
        })())
    )

    assert lmu_decision == {"show_widgets": True}
    assert rf2_decision == {"show_widgets": True}
    assert mock_decision == {"show_widgets": False}
    assert inactive_decision == {"show_widgets": False}
    lmu_rf2_plugin._service_instance = None


def test_connector_handoff_reapplies_family_decision_when_internal_state_changes(monkeypatch) -> None:
    """Connector handoff should re-evaluate plugin decisions when family state changes behind a stable live source."""

    service = _FakeStickyLiveConnectorService()
    lmu_rf2_plugin._service_instance = cast(Any, service)

    monkeypatch.setattr(
        "runtimeV2.connectors.policy.load_connector_service",
        lambda module_name, class_name: service,
    )
    monkeypatch.setattr(
        "runtimeV2.connectors.game_detector.psutil.process_iter",
        lambda attrs=None: [type("Proc", (), {"info": {"name": "LeMansUltimate.exe"}})()],
    )

    runtime, _bus = _make_runtime(
        {
            "LMU_RF2_Connector": ConnectorManifest(
                games=[
                    ConnectorGameDecl(id="lmu", detect_names=["Le Mans Ultimate"]),
                    ConnectorGameDecl(id="rf2", detect_names=["rFactor2"]),
                ],
                service=ConnectorServiceDecl(
                    module="plugins.LMU_RF2_Connector.plugin",
                    class_name="LMURF2Connector",
                ),
                runtime=ConnectorRuntimeDecl(game_state_hook="update_game_state"),
            )
        }
    )

    assert startup_connectors(cast(Any, runtime)) == StartupResult(ok=True)
    scheduler_write = cast(SchedulerWrite, runtime.registered_capabilities["scheduler_write"])
    read = cast(ConnectorRead, runtime.registered_capabilities["connector_read"])
    widget_config_write = cast(_FakeWidgetConfigWrite, runtime._capabilities["widget_config_write"])

    scheduler_write.tick(5000)
    assert read.show_widgets("LMU_RF2_Connector") is True
    assert widget_config_write.global_visible is True

    scheduler_write.tick(5020)
    assert read.show_widgets("LMU_RF2_Connector") is False
    assert widget_config_write.global_visible is False
    lmu_rf2_plugin._service_instance = None


def test_connector_live_mode_hides_widgets_when_detected_game_is_lost(monkeypatch) -> None:
    """Connector live mode should fall back to probe and hide widgets when game detection is lost."""

    service = _FakeExitLiveConnectorService()
    lmu_rf2_plugin._service_instance = cast(Any, service)
    process_names = [
        [type("Proc", (), {"info": {"name": "LeMansUltimate.exe"}})()],
        [],
    ]

    monkeypatch.setattr(
        "runtimeV2.connectors.policy.load_connector_service",
        lambda module_name, class_name: service,
    )
    monkeypatch.setattr(
        "runtimeV2.connectors.game_detector.psutil.process_iter",
        lambda attrs=None: process_names.pop(0),
    )

    runtime, _bus = _make_runtime(
        {
            "LMU_RF2_Connector": ConnectorManifest(
                games=[
                    ConnectorGameDecl(id="lmu", detect_names=["Le Mans Ultimate"]),
                    ConnectorGameDecl(id="rf2", detect_names=["rFactor2"]),
                ],
                service=ConnectorServiceDecl(
                    module="plugins.LMU_RF2_Connector.plugin",
                    class_name="LMURF2Connector",
                ),
                runtime=ConnectorRuntimeDecl(game_state_hook="update_game_state"),
            )
        }
    )

    assert startup_connectors(cast(Any, runtime)) == StartupResult(ok=True)
    scheduler_write = cast(SchedulerWrite, runtime.registered_capabilities["scheduler_write"])
    scheduler_read = cast(SchedulerRead, runtime.registered_capabilities["scheduler_read"])
    read = cast(ConnectorRead, runtime.registered_capabilities["connector_read"])
    widget_config_write = cast(_FakeWidgetConfigWrite, runtime._capabilities["widget_config_write"])

    scheduler_write.tick(5000)
    assert read.show_widgets("LMU_RF2_Connector") is True
    assert widget_config_write.global_visible is True

    scheduler_write.tick(5020)
    assert read.show_widgets("LMU_RF2_Connector") is False
    assert widget_config_write.global_visible is False
    jobs = {job.job_id: job for job in scheduler_read.jobs()}
    assert jobs["connectors.LMU_RF2_Connector.probe_game_state"].enabled is True
    assert jobs["connectors.LMU_RF2_Connector.live_poll"].enabled is False
    lmu_rf2_plugin._service_instance = None

