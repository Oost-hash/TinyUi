"""Tests for the runtime V2 boot entry point."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast

import bootv2
from runtimeV2.connectors.schemas.manifest import ConnectorManifest
from shared_runtime_host.capabilities.ui_api import ManifestQmlCapability
from runtimeV2.capabilities.runtime_shutdown import RuntimeShutdown
from runtimeV2.events.capabilities.event_read import EventRead
from runtimeV2.events.contracts import EventBus, EventType
from runtimeV2.events.event_registry import EventRegistry
from runtimeV2.events.startup import EventsStartupResult
from runtimeV2.host.contracts import HostAppIdentity
from runtimeV2.host.capabilities.main_window_read import MainWindowRead
from runtimeV2.host.contracts import HostShell
from runtimeV2.manifest.capabilities.ui_read import ManifestUiRead
from runtimeV2.manifest.registry import ManifestRegistry
from runtimeV2.persistence.capabilities.widget_config_read import WidgetConfigRead
from runtimeV2.persistence.capabilities.widget_config_write import WidgetConfigWrite
from runtimeV2.persistence.contracts import PersistencePaths
from runtimeV2.persistence.widget_config import WidgetConfigStore
from runtimeV2.schemas.startup import StartupResult
from runtimeV2.ui.contracts import QmlPropertyPlan, UIChromeModel, UIRenderStatus
from runtimeV2.ui.contracts import UIWindowRecordsChangedData
from runtimeV2.ui.capabilities.chrome_model_read import UIChromeModelRead
from runtimeV2.ui.capabilities.window_actions_write import WindowActionsWrite
from runtimeV2.ui.capabilities.window_records_read import WindowRecordsRead
from runtimeV2.ui.projection import project_ui_window_records
from runtimeV2.ui.schemas.manifest import AppManifest, ChromePolicy, UiManifest
from runtimeV2.ui.startup import UIStartupResult
from runtimeV2.widgets.capabilities.widget_visibility_read import WidgetVisibilityRead
from runtimeV2.widgets.capabilities.widget_visibility_write import WidgetVisibilityWrite
from runtimeV2.widgets.capabilities.widget_records_read import WidgetRecordsRead
from runtimeV2.widgets.store import WidgetRecordsStore
from ui_api.runtime_host import build_runtime_qml_properties, start_runtime_host


@dataclass(frozen=True)
class _FakeRuntimeResult:
    runtime: object


class _FakeApp:
    def __init__(self) -> None:
        self.exec_called = False
        self.aboutToQuit = _FakeSignal()
        self.properties: dict[str, object] = {}

    def exec(self) -> int:
        self.exec_called = True
        return 0

    def setProperty(self, key: str, value: object) -> None:
        self.properties[key] = value

    def quit(self) -> None:
        self.properties["quit_called"] = True


class _FakeSignal:
    def __init__(self) -> None:
        self._callbacks: list[object] = []

    def connect(self, callback) -> None:
        self._callbacks.append(callback)


class _FakeCapabilityRuntime:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []

    def capability(self, name: str, capability_type: type) -> object:
        self.calls.append((name, capability_type.__name__))
        return f"{name}:capability"


class _FakeShutdown:
    def __init__(self, events: EventsStartupResult) -> None:
        self.calls: list[str] = []
        self._events = events

    def begin_shutdown(self, reason: str = "app_quit") -> bool:
        self.calls.append(reason)
        self._events.bus.emit_typed(EventType.RUNTIME_SHUTDOWN, data=None, source="runtime")
        return True


class _FakeUiRuntime:
    def __init__(self) -> None:
        self._events = EventsStartupResult(
            bus=EventBus(),
            registry=EventRegistry(),
            event_read=EventRead(EventRegistry()),
        )
        self.shutdown = _FakeShutdown(self._events)
        self._ui_result = UIStartupResult(
            records=[],
            render_status=UIRenderStatus(render_ready=True, main_window_id="tinyui.main"),
            chrome_model=cast(Any, SimpleNamespace()),
            qml_property_plan=[],
            capabilities=cast(Any, SimpleNamespace()),
        )
        self._main_window = MainWindowRead(
            HostShell(
                host_plugin_id="tinyui",
                host_manifest=cast(Any, SimpleNamespace()),
                main_window=AppManifest(
                    id="tinyui.main",
                    title="TinyUI",
                    surface=Path("surface.qml"),
                    chrome=ChromePolicy(),
                ),
                identity=HostAppIdentity(
                    app_id="tinyui",
                    app_version="0.5.0",
                    app_title="TinyUI",
                    app_icon="",
                ),
            )
        )
        self._widget_records = WidgetRecordsRead(WidgetRecordsStore())
        self._ui_chrome = UIChromeModelRead(
            UIChromeModel(
                menu_items=[],
                plugin_menu_items=[],
                plugin_menu_label="",
                statusbar_items=[],
                tabs=[],
                active_plugin_id="",
                status_active_label="",
            )
        )
        manifest_registry = ManifestRegistry()
        manifest_registry.register_manifest(
            manifest=cast(
                Any,
                SimpleNamespace(
                    plugin_id="tinyui",
                    plugin_type="host",
                    version="0.5.0",
                    author="",
                    description="",
                    icon="",
                    requires=[],
                    ui=UiManifest(
                        windows=[
                            AppManifest(id="tinyui.main", title="TinyUI", surface=Path("surface.qml")),
                            AppManifest(id="devtools.main", title="DevTools", surface=Path("devtools.qml")),
                        ]
                    ),
                ),
            ),
            manifest_path=Path("tinyui/manifest.toml"),
            resource_root=Path("."),
            source="test",
        )
        self._manifest_ui = ManifestUiRead(manifest_registry)
        projected_records = project_ui_window_records(
            ui_manifest_read=self._manifest_ui,
            main_window_read=self._main_window,
        )
        self._window_records = WindowRecordsRead(projected_records)
        self._window_actions = WindowActionsWrite(self._window_records, "tinyui.main")
        widget_store = WidgetConfigStore(
            PersistencePaths(
                base_dir=Path("."),
                config_root=Path("."),
                cache_dir=Path("."),
                logs_dir=Path("."),
                bootstrap_path=Path("bootstrap.toml"),
                config_sets_path=Path("config_sets.json"),
            ),
            "default",
        )
        self._widget_visibility_read = WidgetVisibilityRead(WidgetConfigRead(widget_store))
        self._widget_visibility_write = WidgetVisibilityWrite(WidgetConfigWrite(widget_store))
        self._widget_visibility_write.set_global_visible(True)

    def domain_result(self, name: str, _result_type: type[Any]) -> Any:
        if name == "ui":
            return self._ui_result
        if name == "events":
            return self._events
        raise KeyError(name)

    def capability(self, name: str, _capability_type: type[Any]) -> Any:
        if name == "main_window_read":
            return self._main_window
        if name == "shutdown":
            return self.shutdown
        if name == "widget_records_read":
            return self._widget_records
        if name == "window_records_read":
            return self._window_records
        if name == "window_actions_write":
            return self._window_actions
        if name == "ui_chrome_model_read":
            return self._ui_chrome
        if name == "manifest_ui_read":
            return self._manifest_ui
        if name == "widget_visibility_read":
            return self._widget_visibility_read
        if name == "widget_visibility_write":
            return self._widget_visibility_write
        raise KeyError(name)


def test_bootv2_returns_zero_when_runtime_v2_is_render_ready(monkeypatch) -> None:
    """bootv2 should succeed once runtime V2 exposes a render-ready UI handoff."""

    app = _FakeApp()
    monkeypatch.setattr(bootv2, "startup_runtime_v2", lambda: StartupResult(ok=True))
    monkeypatch.setattr(bootv2, "get_runtime_v2_result", lambda: _FakeRuntimeResult(object()))
    monkeypatch.setattr(bootv2, "create_application", lambda: app)
    monkeypatch.setattr(bootv2, "create_engine", lambda: object())
    monkeypatch.setattr(
        bootv2,
        "start_runtime_host",
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
        "start_runtime_host",
        lambda **_kwargs: (None, StartupResult(ok=False, error_message="missing main window")),
    )

    assert bootv2.main() == 1
    assert "missing main window" in capsys.readouterr().err


def test_runtime_host_builds_qml_properties_from_ui_schema() -> None:
    """The ui_api host should apply the runtime V2 QML property schema."""

    runtime = _FakeCapabilityRuntime()
    ui_result = cast(Any, SimpleNamespace(qml_property_plan=[
        QmlPropertyPlan("manifest_read", "manifestRead"),
        QmlPropertyPlan("settings_read", "settingsRead"),
    ]))

    properties = build_runtime_qml_properties(cast(Any, runtime), cast(UIStartupResult, ui_result))

    assert isinstance(properties["manifestRead"], ManifestQmlCapability)
    assert properties["settingsRead"] == "settings_read:capability"
    assert runtime.calls == [
        ("manifest_read", "ManifestRead"),
        ("settings_read", "SettingsRead"),
    ]


def test_runtime_host_close_action_requests_runtime_shutdown(monkeypatch) -> None:
    """The ui_api close action should request runtime shutdown through the V2 capability."""

    app = _FakeApp()
    runtime = _FakeUiRuntime()
    close_calls: list[str] = []

    class _FakeWindow:
        def __init__(self) -> None:
            self.destroyed = _FakeSignal()

        def close(self) -> None:
            close_calls.append("closed")

    monkeypatch.setattr(
        "ui_api.runtime_host.open_window",
        lambda *_args, **_kwargs: SimpleNamespace(qml_window=_FakeWindow(), keepalive=()),
    )

    result, startup_result = start_runtime_host(
        app=app,
        engine=object(),
        runtime=cast(Any, runtime),
    )

    assert startup_result.ok
    assert result is not None

    result.actions.trigger("close")

    assert runtime.shutdown.calls == ["main_window_close"]
    assert close_calls == ["closed"]


def test_runtime_host_open_action_uses_runtime_window_actions(monkeypatch) -> None:
    """The ui_api host should open runtime-declared windows through action mapping."""

    app = _FakeApp()
    runtime = _FakeUiRuntime()
    opened: list[str] = []

    class _FakeWindow:
        def __init__(self) -> None:
            self.destroyed = _FakeSignal()

        def close(self) -> None:
            return None

    def _open_window(manifest, *_args, **_kwargs):
        opened.append(manifest.id)
        return SimpleNamespace(qml_window=_FakeWindow(), keepalive=())

    monkeypatch.setattr("ui_api.runtime_host.open_window", _open_window)

    result, startup_result = start_runtime_host(
        app=app,
        engine=object(),
        runtime=cast(Any, runtime),
    )

    assert startup_result.ok
    assert result is not None

    result.actions.trigger("open:devtools.main")

    assert opened == ["tinyui.main", "devtools.main"]


def test_runtime_host_widget_visibility_toggle_uses_runtime_capability(monkeypatch) -> None:
    """The ui_api host should toggle widget visibility through runtime-owned capabilities."""

    app = _FakeApp()
    runtime = _FakeUiRuntime()

    class _FakeWindow:
        def __init__(self) -> None:
            self.destroyed = _FakeSignal()

        def close(self) -> None:
            return None

    monkeypatch.setattr(
        "ui_api.runtime_host.open_window",
        lambda *_args, **_kwargs: SimpleNamespace(qml_window=_FakeWindow(), keepalive=()),
    )

    result, startup_result = start_runtime_host(
        app=app,
        engine=object(),
        runtime=cast(Any, runtime),
    )

    assert startup_result.ok
    assert result is not None
    assert runtime._widget_visibility_read.global_visible() is True

    result.actions.trigger("widgetVisibility.toggle")

    assert runtime._widget_visibility_read.global_visible() is False


def test_ui_startup_emits_window_record_change_before_ready(monkeypatch) -> None:
    """UI startup should emit a typed window-record update alongside readiness."""

    from runtimeV2.ui.startup import startup_ui

    class _FakeRuntime:
        def __init__(self) -> None:
            self.events = EventsStartupResult(
                bus=EventBus(),
                registry=EventRegistry(),
                event_read=EventRead(EventRegistry()),
            )
            self.records = []
            self.capabilities: dict[str, object] = {
                "main_window_read": _FakeUiRuntime()._main_window,
                "manifest_ui_read": ManifestUiRead(ManifestRegistry()),
                "plugin_active_read": cast(Any, SimpleNamespace(get_active_plugin=lambda: "")),
            }
            self.result: object | None = None

        def domain_result(self, name: str, _result_type: type[Any]) -> Any:
            if name == "events":
                return self.events
            raise KeyError(name)

        def capability(self, name: str, _capability_type: type[Any]) -> Any:
            return self.capabilities[name]

        def register_capability(self, name: str, capability: object) -> None:
            self.capabilities[name] = capability

        def register_domain_result(self, name: str, result: object) -> None:
            self.result = result

    monkeypatch.setattr("runtimeV2.ui.startup.project_ui_window_records", lambda **_kwargs: [])
    monkeypatch.setattr(
        "runtimeV2.ui.startup.determine_render_status",
        lambda **_kwargs: UIRenderStatus(render_ready=True, main_window_id="tinyui.main"),
    )
    monkeypatch.setattr(
        "runtimeV2.ui.startup.build_ui_chrome_model",
        lambda **_kwargs: UIChromeModel(
            menu_items=[],
            plugin_menu_items=[],
            plugin_menu_label="",
            statusbar_items=[],
            tabs=[],
            active_plugin_id="",
            status_active_label="",
        ),
    )

    runtime = _FakeRuntime()
    result = startup_ui(cast(Any, runtime))

    assert result.ok
    window_events = runtime.events.bus.get_history(EventType.UI_WINDOW_RECORDS_CHANGED)
    ready_events = runtime.events.bus.get_history(EventType.UI_READY)
    assert len(window_events) == 1
    assert window_events[0].data == UIWindowRecordsChangedData(window_count=0)
    assert len(ready_events) == 1
