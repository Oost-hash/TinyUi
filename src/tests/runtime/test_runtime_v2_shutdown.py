"""Tests for runtime V2 shutdown orchestration."""

from __future__ import annotations

from runtimeV2.capabilities.runtime_globals import RuntimeGlobals
from runtimeV2.capabilities.runtime_shutdown import RuntimeShutdown
from runtimeV2.events.contracts import EventType
from runtimeV2.events.startup import EventsStartupResult, startup_events
from runtimeV2.register_capabilities import register_runtime_capabilities
from runtimeV2.register_globals import register_runtime_globals
from runtimeV2.runtime import RuntimeV2
from runtimeV2.schemas.events import RuntimeShutdownData
from runtimeV2.schemas.startup import startup_ok


def test_runtime_shutdown_is_registered_as_global_read_and_write_capability() -> None:
    """Shutdown global should resolve to the runtime shutdown capability."""

    runtime = RuntimeV2()
    register_runtime_capabilities(runtime)
    register_runtime_globals(runtime)

    globals_capability = runtime.capability("globals", RuntimeGlobals)
    shutdown_read = globals_capability.read_global("shutdown", RuntimeShutdown)
    shutdown_write = globals_capability.write_global("shutdown", RuntimeShutdown)

    assert shutdown_read is shutdown_write
    assert not shutdown_read.shutdown_requested()


def test_runtime_shutdown_emits_once_and_records_reason() -> None:
    """Runtime shutdown should emit one typed event and keep the first reason."""

    runtime = RuntimeV2()
    register_runtime_capabilities(runtime)
    register_runtime_globals(runtime)
    runtime.register_domain("events", startup_events)

    assert runtime.start_domain("events").ok

    shutdown = runtime.capability("shutdown", RuntimeShutdown)

    assert shutdown.begin_shutdown("test_close")
    assert not shutdown.begin_shutdown("second_call_should_be_ignored")

    events = runtime.domain_result("events", EventsStartupResult)
    history = events.bus.get_history(EventType.RUNTIME_SHUTDOWN)

    assert shutdown.shutdown_requested()
    assert shutdown.shutdown_reason() == "test_close"
    assert len(history) == 1
    assert isinstance(history[0].data, RuntimeShutdownData)
    assert history[0].data.reason == "test_close"


def test_runtime_shutdown_runs_stop_hooks_in_reverse_domain_order() -> None:
    """Runtime shutdown should stop ready domains in reverse registration order."""

    runtime = RuntimeV2()
    register_runtime_capabilities(runtime)
    register_runtime_globals(runtime)
    runtime.register_domain("events", startup_events)
    runtime.register_domain("alpha", lambda _runtime: startup_ok())
    runtime.register_domain("beta", lambda _runtime: startup_ok())

    assert runtime.start_domain("events").ok
    assert runtime.start_domain("alpha").ok
    assert runtime.start_domain("beta").ok

    calls: list[str] = []
    runtime.register_stop_hook("alpha", lambda: calls.append("alpha"))
    runtime.register_stop_hook("beta", lambda: calls.append("beta"))

    shutdown = runtime.capability("shutdown", RuntimeShutdown)
    shutdown.begin_shutdown("test_close")

    assert calls == ["beta", "alpha"]
    assert runtime.domain_status("alpha").value == "stopped"
    assert runtime.domain_status("beta").value == "stopped"
