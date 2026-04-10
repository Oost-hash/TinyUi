"""Tests for runtime V2 scheduler."""

from __future__ import annotations

from typing import Any, cast

from runtimeV2.events.capabilities.event_read import EventRead
from runtimeV2.events.contracts import EventBus, EventType
from runtimeV2.events.event_registry import EventRegistry
from runtimeV2.events.startup_shutdown.startup import EventsStartupResult
from runtimeV2.scheduler.capabilities.scheduler_read import SchedulerRead
from runtimeV2.scheduler.capabilities.scheduler_write import SchedulerWrite
from runtimeV2.scheduler.capabilities.scheduler_clock_read import SchedulerClockRead
from runtimeV2.scheduler.capabilities.scheduler_clock_write import SchedulerClockWrite
from runtimeV2.scheduler.startup_shutdown.startup import SchedulerStartupResult, startup_scheduler
from runtimeV2.schemas.startup import StartupResult


class _FakeRuntime:
    def __init__(self) -> None:
        self.events = EventsStartupResult(
            bus=EventBus(),
            registry=EventRegistry(),
            event_read=EventRead(EventRegistry()),
        )
        self.capabilities: dict[str, object] = {}
        self.results: dict[str, object] = {}
        self.stop_hooks: dict[str, list[object]] = {}

    def domain_result(self, name: str, _result_type: type[Any]) -> Any:
        if name == "events":
            return self.events
        raise KeyError(name)

    def register_capability(self, name: str, capability: object) -> None:
        self.capabilities[name] = capability

    def register_domain_result(self, name: str, result: object) -> None:
        self.results[name] = result

    def register_stop_hook(self, owner: str, hook) -> None:
        self.stop_hooks.setdefault(owner, []).append(hook)


def test_startup_scheduler_registers_capabilities_and_stop_hook() -> None:
    """Scheduler startup should expose read/write capabilities and a stop hook."""

    runtime = _FakeRuntime()

    assert startup_scheduler(cast(Any, runtime)) == StartupResult(ok=True)

    assert isinstance(runtime.capabilities["scheduler_read"], SchedulerRead)
    assert isinstance(runtime.capabilities["scheduler_write"], SchedulerWrite)
    assert isinstance(runtime.capabilities["scheduler_clock_read"], SchedulerClockRead)
    assert isinstance(runtime.capabilities["scheduler_clock_write"], SchedulerClockWrite)
    assert "scheduler" in runtime.stop_hooks
    assert isinstance(runtime.results["scheduler"], SchedulerStartupResult)


def test_scheduler_tick_runs_due_job_and_emits_events() -> None:
    """Scheduler should run due jobs on ticks and emit scheduler events."""

    runtime = _FakeRuntime()
    assert startup_scheduler(cast(Any, runtime)) == StartupResult(ok=True)
    write = cast(SchedulerWrite, runtime.capabilities["scheduler_write"])
    read = cast(SchedulerRead, runtime.capabilities["scheduler_read"])
    calls: list[str] = []

    write.register_job(
        job_id="scheduler.test_job",
        owner_domain="tests",
        interval_ms=20,
        callback=lambda: calls.append("tick"),
    )

    assert read.minimum_interval_ms() == 20
    assert write.tick(0) == ["scheduler.test_job"]
    assert write.tick(10) == []
    assert write.tick(20) == ["scheduler.test_job"]
    assert calls == ["tick", "tick"]

    history = runtime.events.bus.get_history()
    assert [event.type for event in history] == [
        EventType.SCHEDULER_JOB_REGISTERED,
        EventType.SCHEDULER_TICK,
        EventType.SCHEDULER_TICK,
        EventType.SCHEDULER_TICK,
    ]


def test_scheduler_clock_lock_wins_and_unlocked_highest_cadence_wins() -> None:
    """Scheduler central clock should combine requests and respect locks."""

    runtime = _FakeRuntime()
    assert startup_scheduler(cast(Any, runtime)) == StartupResult(ok=True)
    read = cast(SchedulerClockRead, runtime.capabilities["scheduler_clock_read"])
    write = cast(SchedulerClockWrite, runtime.capabilities["scheduler_clock_write"])

    assert read.clock_mode() == "idle"
    assert read.clock_interval_ms() == 5000

    assert write.request_clock_mode("ui", "normal") is True
    assert read.clock_mode() == "normal"
    assert read.clock_interval_ms() == 1000

    assert write.request_clock_mode("mock", "live") is True
    assert read.clock_mode() == "live"
    assert read.clock_interval_ms() == 20
    assert read.clock_locked_by() is None

    assert write.request_clock_mode("connectors", "idle", lock=True) is True
    assert read.clock_mode() == "idle"
    assert read.clock_locked_by() == "connectors"

    assert write.request_clock_mode("mock", "live") is False
    assert read.clock_mode() == "idle"

    assert write.release_clock_lock("mock") is False
    assert write.release_clock_lock("connectors") is True
    assert read.clock_mode() == "live"

    history = runtime.events.bus.get_history(EventType.SCHEDULER_CLOCK_UPDATED)
    assert [event.data.mode for event in history] == ["normal", "live", "idle", "live"]
