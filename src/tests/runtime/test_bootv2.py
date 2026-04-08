"""Tests for the runtime V2 boot entry point."""

from __future__ import annotations

from dataclasses import dataclass
from types import SimpleNamespace
from typing import Any, cast

import bootv2
from runtimeV2.schemas.startup import StartupResult
from runtimeV2.ui.contracts import QmlPropertyPlan
from runtimeV2.ui.startup import UIStartupResult
from ui_api.runtime_v2_host import build_runtime_v2_qml_properties


@dataclass(frozen=True)
class _FakeRuntimeResult:
    runtime: object


class _FakeApp:
    def __init__(self) -> None:
        self.exec_called = False

    def exec(self) -> int:
        self.exec_called = True
        return 0


class _FakeCapabilityRuntime:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []

    def capability(self, name: str, capability_type: type) -> object:
        self.calls.append((name, capability_type.__name__))
        return f"{name}:capability"


def test_bootv2_returns_zero_when_runtime_v2_is_render_ready(monkeypatch) -> None:
    """bootv2 should succeed once runtime V2 exposes a render-ready UI handoff."""

    app = _FakeApp()
    monkeypatch.setattr(bootv2, "startup_runtime_v2", lambda: StartupResult(ok=True))
    monkeypatch.setattr(bootv2, "get_runtime_v2_result", lambda: _FakeRuntimeResult(object()))
    monkeypatch.setattr(bootv2, "create_application", lambda: app)
    monkeypatch.setattr(bootv2, "create_engine", lambda: object())
    monkeypatch.setattr(
        bootv2,
        "start_runtime_v2_host",
        lambda **_kwargs: (SimpleNamespace(), StartupResult(ok=True)),
    )

    assert bootv2.main() == 0
    assert app.exec_called


def test_bootv2_returns_error_when_runtime_v2_startup_fails(monkeypatch, capsys) -> None:
    """bootv2 should report startup failures from runtime V2."""

    monkeypatch.setattr(bootv2, "startup_runtime_v2", lambda: StartupResult(ok=False, error_message="broken"))
    monkeypatch.setattr(bootv2, "create_application", lambda: _FakeApp())
    monkeypatch.setattr(bootv2, "create_engine", lambda: object())

    assert bootv2.main() == 1
    assert "broken" in capsys.readouterr().err


def test_bootv2_returns_error_when_ui_api_host_fails(monkeypatch, capsys) -> None:
    """bootv2 should report ui_api host failures."""

    monkeypatch.setattr(bootv2, "startup_runtime_v2", lambda: StartupResult(ok=True))
    monkeypatch.setattr(bootv2, "get_runtime_v2_result", lambda: _FakeRuntimeResult(object()))
    monkeypatch.setattr(bootv2, "create_application", lambda: _FakeApp())
    monkeypatch.setattr(bootv2, "create_engine", lambda: object())
    monkeypatch.setattr(
        bootv2,
        "start_runtime_v2_host",
        lambda **_kwargs: (None, StartupResult(ok=False, error_message="missing main window")),
    )

    assert bootv2.main() == 1
    assert "missing main window" in capsys.readouterr().err


def test_runtime_v2_host_builds_qml_properties_from_ui_schema() -> None:
    """The ui_api host should apply the runtime V2 QML property schema."""

    runtime = _FakeCapabilityRuntime()
    ui_result = cast(Any, SimpleNamespace(qml_property_plan=[
        QmlPropertyPlan("manifest_read", "pluginRead"),
        QmlPropertyPlan("settings_read", "settingsRead"),
    ]))

    properties = build_runtime_v2_qml_properties(cast(Any, runtime), cast(UIStartupResult, ui_result))

    assert properties == {
        "pluginRead": "manifest_read:capability",
        "settingsRead": "settings_read:capability",
    }
    assert runtime.calls == [
        ("manifest_read", "ManifestRead"),
        ("settings_read", "SettingsRead"),
    ]
