"""Tests for shared_runtime_host startup bridge."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any, cast

from runtimeV2.events.capabilities.event_registration_write import EventRegistrationWrite
from runtimeV2.events.contracts import EventBus
from runtimeV2.events.event_registry import EventRegistry
from runtimeV2.schemas.startup import StartupResult
from shared_runtime_host.registry import SharedRuntimeHostRegistry, create_shared_runtime_host_registry
from shared_runtime_host.startup_shutdown.startup import startup_shared_runtime_host


class _FakeRuntime:
    def __init__(self) -> None:
        self.event_registration_write = EventRegistrationWrite(EventRegistry(), EventBus())

    def capability(self, name: str, _capability_type: type[Any]) -> Any:
        if name == "event_registration_write":
            return self.event_registration_write
        raise KeyError(name)


class _FakeApp:
    def __init__(self) -> None:
        self.properties: dict[str, object] = {}

    def setProperty(self, key: str, value: object) -> None:
        self.properties[key] = value


def test_shared_runtime_host_startup_starts_api_hosts_with_shared_registry(monkeypatch) -> None:
    """Shared host startup should create one registry and pass it to both API hosts."""

    import shared_runtime_host.startup_shutdown.startup as startup

    app = _FakeApp()
    runtime = _FakeRuntime()
    registries: list[SharedRuntimeHostRegistry] = []

    monkeypatch.setattr(startup, "start_runtime_scheduler_clock", lambda *_args, **_kwargs: SimpleNamespace())
    monkeypatch.setattr(startup, "register_widget_host", lambda _registry: None)
    monkeypatch.setattr(startup, "register_ui_runtime_host", lambda registry: registry.register_capability("ui", object()))
    monkeypatch.setattr(
        startup,
        "register_widget_runtime_host",
        lambda registry: registry.register_capability("widget", object()),
    )

    def _start_runtime_host(**kwargs):
        registries.append(kwargs["host_registry"])
        return SimpleNamespace(), StartupResult(ok=True)

    def _startup_widget_api(**kwargs):
        registries.append(kwargs["host_registry"])
        return SimpleNamespace(), StartupResult(ok=True)

    monkeypatch.setattr(startup, "start_runtime_host", _start_runtime_host)
    monkeypatch.setattr(startup, "startup_widget_api", _startup_widget_api)

    result, startup_result = startup_shared_runtime_host(app, object(), runtime)  # type: ignore[arg-type]

    assert startup_result.ok
    assert result is not None
    assert registries == [result.registry, result.registry]
    assert app.properties["_sharedRuntimeHost"] is result


def test_shared_runtime_host_startup_returns_failure_when_ui_host_fails(monkeypatch) -> None:
    """Shared host startup should fail when a child API host fails."""

    import shared_runtime_host.startup_shutdown.startup as startup

    monkeypatch.setattr(startup, "start_runtime_scheduler_clock", lambda *_args, **_kwargs: SimpleNamespace())
    monkeypatch.setattr(startup, "register_widget_host", lambda _registry: None)
    monkeypatch.setattr(startup, "register_ui_runtime_host", lambda _registry: None)
    monkeypatch.setattr(startup, "register_widget_runtime_host", lambda _registry: None)
    monkeypatch.setattr(
        startup,
        "start_runtime_host",
        lambda **_kwargs: (None, StartupResult(ok=False, error_message="ui failed")),
    )

    result, startup_result = startup_shared_runtime_host(_FakeApp(), object(), _FakeRuntime())  # type: ignore[arg-type]

    assert result is None
    assert startup_result == StartupResult(ok=False, error_message="ui failed")


def test_shared_runtime_host_startup_rolls_back_ui_host_when_widget_host_fails(monkeypatch) -> None:
    """Shared host startup should close partial host state when widget_api startup fails."""

    import shared_runtime_host.startup_shutdown.startup as startup

    driver_calls: list[str] = []
    ui_shutdown_calls: list[str] = []

    class _FakeDriver:
        def stop(self) -> None:
            driver_calls.append("stopped")

    class _FakeShutdown:
        def close_host(self) -> None:
            ui_shutdown_calls.append("closed")

    monkeypatch.setattr(startup, "start_runtime_scheduler_clock", lambda *_args, **_kwargs: _FakeDriver())
    monkeypatch.setattr(startup, "register_widget_host", lambda _registry: None)
    monkeypatch.setattr(startup, "register_ui_runtime_host", lambda _registry: None)
    monkeypatch.setattr(startup, "register_widget_runtime_host", lambda _registry: None)
    monkeypatch.setattr(
        startup,
        "start_runtime_host",
        lambda **_kwargs: (SimpleNamespace(shutdown=_FakeShutdown()), StartupResult(ok=True)),
    )
    monkeypatch.setattr(
        startup,
        "startup_widget_api",
        lambda **_kwargs: (None, StartupResult(ok=False, error_message="widget failed")),
    )

    result, startup_result = startup_shared_runtime_host(_FakeApp(), object(), _FakeRuntime())  # type: ignore[arg-type]

    assert result is None
    assert startup_result == StartupResult(ok=False, error_message="widget failed")
    assert ui_shutdown_calls == ["closed"]
    assert driver_calls == ["stopped"]


def test_shared_runtime_host_registry_rejects_duplicate_capability_names() -> None:
    """Shared host registry should not silently overwrite capabilities."""

    registry = create_shared_runtime_host_registry(cast(Any, SimpleNamespace()))
    registry.register_capability("widget_host", object())

    try:
        registry.register_capability("widget_host", object())
    except ValueError as exc:
        assert "already registered" in str(exc)
    else:
        raise AssertionError("Expected duplicate capability registration to fail")
