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
from typing import Any, cast

from plugins.LMU_RF2_Connector.runtime import ConnectorRuntime
from runtimeV2.capabilities.runtime_globals import RuntimeGlobals
from runtimeV2.connectors.capabilities.connector_read import ConnectorRead
from runtimeV2.connectors.capabilities.connector_write import ConnectorWrite
from runtimeV2.connectors.contracts import ConnectorSourceChangedData
from runtimeV2.connectors.policy import unregister_connector_service
from runtimeV2.connectors.schemas.manifest import ConnectorManifest, ConnectorServiceDecl
from runtimeV2.scheduler.capabilities.scheduler_write import SchedulerWrite
from runtimeV2.scheduler.capabilities.scheduler_read import SchedulerRead
from runtimeV2.scheduler.driver import SchedulerDriver
from runtimeV2.scheduler.registry import SchedulerRegistry
from runtimeV2.connectors.startup_shutdown.startup import startup_connectors, ConnectorsStartupResult
from runtimeV2.events.contracts import EventBus, EventType
from runtimeV2.events.event_registry import EventRegistry
from runtimeV2.events.startup_shutdown.startup import EventsStartupResult
from runtimeV2.globals import GlobalRegistration
from runtimeV2.manifest.capabilities.connector_read import ManifestConnectorRead
from runtimeV2.schemas.startup import StartupResult


class _FakeConnectorService:
    def __init__(self) -> None:
        self.open_called = False
        self.update_calls = 0
        self.requested: list[tuple[str, str]] = []
        self.released: list[str] = []
        self.closed = False

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
        },
        registered_capabilities=registered_capabilities,
        registered_results={},
        registered_globals={},
    )
    registered_capabilities["globals"] = RuntimeGlobals(cast(Any, runtime))
    scheduler_registry = SchedulerRegistry()
    scheduler_driver = SchedulerDriver(scheduler_registry, bus)
    registered_capabilities["scheduler_write"] = SchedulerWrite(scheduler_registry, scheduler_driver, bus)
    registered_capabilities["scheduler_read"] = SchedulerRead(scheduler_registry)
    return runtime, bus


class _FakeSettingsRead:
    def get(self, namespace: str, key: str) -> int | None:
        if namespace == "tinyui" and key == "connector_poll_interval_ms":
            return 20
        return None


def test_startup_connectors_registers_declared_services(monkeypatch) -> None:
    """Connectors startup should load and register manifest-declared services."""

    service = _FakeConnectorService()
    monkeypatch.setattr(
        "runtimeV2.connectors.policy.load_connector_service",
        lambda module_name, class_name: service,
    )

    runtime, bus = _make_runtime(
        {
            "iracing": ConnectorManifest(
                service=ConnectorServiceDecl(module="plugins.iracing", class_name="IRacingService")
            )
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
    scheduler_write.tick(20)
    assert service.update_calls == 1
    scheduler_write.tick(1000)
    assert service.update_calls == 1
    scheduler_write.tick(1020)
    assert service.update_calls == 2
    scheduler_jobs = cast(SchedulerRead, runtime.registered_capabilities["scheduler_read"]).jobs()
    assert [job.job_id for job in scheduler_jobs] == [
        "connectors.iracing.probe_game_state",
        "connectors.iracing.live_poll",
    ]
    assert scheduler_jobs[0].enabled is True
    assert scheduler_jobs[1].enabled is False
    assert [event.type for event in bus.get_history()] == [
        EventType.CONNECTOR_SERVICE_REGISTERED,
        EventType.CONNECTOR_SERVICE_UPDATED,
        EventType.SCHEDULER_JOB_REGISTERED,
        EventType.SCHEDULER_JOB_REGISTERED,
        EventType.CONNECTOR_SERVICE_UPDATED,
        EventType.SCHEDULER_TICK,
        EventType.SCHEDULER_TICK,
        EventType.CONNECTOR_SERVICE_UPDATED,
        EventType.SCHEDULER_TICK,
    ]


def test_connector_write_can_update_all_services(monkeypatch) -> None:
    """Connector write capability should update all active services."""

    services = {
        "iracing": _FakeConnectorService(),
        "acc": _FakeConnectorService(),
    }

    def _load_service(module_name: str, class_name: str) -> _FakeConnectorService:
        return services[module_name]

    monkeypatch.setattr("runtimeV2.connectors.policy.load_connector_service", _load_service)

    runtime, bus = _make_runtime(
        {
            "iracing": ConnectorManifest(service=ConnectorServiceDecl(module="iracing", class_name="Service")),
            "acc": ConnectorManifest(service=ConnectorServiceDecl(module="acc", class_name="Service")),
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
    runtime, _bus = _make_runtime(
        {
            "iracing": ConnectorManifest(
                service=ConnectorServiceDecl(module="plugins.iracing", class_name="IRacingService")
            )
        }
    )

    assert startup_connectors(cast(Any, runtime)) == StartupResult(ok=True)

    scheduler_write = cast(SchedulerWrite, runtime.registered_capabilities["scheduler_write"])
    scheduler_read = cast(SchedulerRead, runtime.registered_capabilities["scheduler_read"])

    scheduler_write.tick(20)

    jobs = {job.job_id: job for job in scheduler_read.jobs()}
    assert jobs["connectors.iracing.probe_game_state"].enabled is False
    assert jobs["connectors.iracing.live_poll"].enabled is True
    assert service.active_source() == "lmu"
    assert service.update_calls == 1

    scheduler_write.tick(40)
    assert service.update_calls == 2


def test_connector_write_emits_source_change_events(monkeypatch) -> None:
    """Connector source requests and releases should emit explicit state-change events."""

    service = _FakeConnectorService()
    monkeypatch.setattr(
        "runtimeV2.connectors.policy.load_connector_service",
        lambda module_name, class_name: service,
    )
    runtime, bus = _make_runtime(
        {
            "iracing": ConnectorManifest(
                service=ConnectorServiceDecl(module="plugins.iracing", class_name="IRacingService")
            )
        }
    )

    assert startup_connectors(cast(Any, runtime)) == StartupResult(ok=True)
    write = cast(ConnectorWrite, runtime.registered_capabilities["connector_write"])

    assert write.request_source("iracing", "devtools", "mock") is True
    assert write.release_source("iracing", "devtools") is True

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


def test_unregister_connector_service_releases_source_and_closes(monkeypatch) -> None:
    """Connector unregister should release runtime mock source and close the service."""

    service = _FakeConnectorService()
    monkeypatch.setattr(
        "runtimeV2.connectors.policy.load_connector_service",
        lambda module_name, class_name: service,
    )
    runtime, bus = _make_runtime(
        {
            "iracing": ConnectorManifest(
                service=ConnectorServiceDecl(module="plugins.iracing", class_name="IRacingService")
            )
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


def test_connector_runtime_prefers_active_real_source_over_mock() -> None:
    """Connector runtime should switch to a live source when it reports active state."""

    lmu = _FakeSource("lmu", kind="shared-memory", game="lmu", active=True)
    rf2 = _FakeSource("rf2", kind="shared-memory", game="rf2", active=False)

    runtime = ConnectorRuntime(cast(Any, lmu), cast(Any, rf2))

    runtime.open()
    runtime.update()

    assert runtime.active_source() == "lmu"
    assert runtime.active_game() == "lmu"


def test_connector_runtime_falls_back_to_mock_without_active_real_source() -> None:
    """Connector runtime should keep mock active when no live source reports activity."""

    lmu = _FakeSource("lmu", kind="shared-memory", game="lmu", active=False)
    rf2 = _FakeSource("rf2", kind="shared-memory", game="rf2", active=False)

    runtime = ConnectorRuntime(cast(Any, lmu), cast(Any, rf2))

    runtime.open()
    runtime.update()

    assert runtime.active_source() == "mock"
    assert runtime.active_game() == "mock"

