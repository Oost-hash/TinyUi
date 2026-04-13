"""Tests for the runtime V2 boot entry point."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast

import bootv2
from runtimeV2.connectors.schemas.manifest import ConnectorManifest, ConnectorRuntimeDecl
from shared_runtime_host.capabilities.ui_api import (
    ConnectorWriteQmlCapability,
    ManifestQmlCapability,
    SettingsQmlCapability,
    WidgetPreviewActions,
)
from runtimeV2.capabilities.runtime_shutdown import RuntimeShutdown
from runtimeV2.capabilities.runtime_globals import RuntimeGlobals
from runtimeV2.events.capabilities.event_read import EventRead
from runtimeV2.events.capabilities.event_registration_write import EventRegistrationWrite
from runtimeV2.events.contracts import EventBus, EventType
from runtimeV2.events.event_registry import EventRegistry
from runtimeV2.events.startup_shutdown.startup import EventsStartupResult
from shared_runtime_host.register_capabilities import register_event_registration_host
from shared_runtime_host.registry import SharedRuntimeHostRegistry, create_shared_runtime_host_registry
from ui_api.register_runtime_host import register_ui_runtime_host
from runtimeV2.host.contracts import HostAppIdentity
from runtimeV2.host.capabilities.main_window_read import MainWindowRead
from runtimeV2.host.contracts import HostShell
from runtimeV2.manifest.capabilities.ui_read import ManifestUiRead
from runtimeV2.manifest.registry import ManifestRegistry
from runtimeV2.persistence.capabilities.widget_config_read import WidgetConfigRead
from runtimeV2.persistence.capabilities.widget_config_write import WidgetConfigWrite
from runtimeV2.persistence.contracts import ConfigSet, PersistencePaths
from runtimeV2.persistence.widget_config import WidgetConfigStore
from runtimeV2.schemas.startup import StartupResult
from runtimeV2.contracts import (
    QmlPropertyPlan,
    UIChromeModel,
    UIRenderStatus,
    UIWindowRecordsChangedData,
)
from runtimeV2.ui.capabilities.chrome_model_read import UIChromeModelRead
from runtimeV2.ui.capabilities.window_actions_write import WindowActionsWrite
from runtimeV2.ui.capabilities.window_records_read import WindowRecordsRead
from runtimeV2.ui.projection import project_ui_window_records
from runtimeV2.ui.schemas.manifest import AppManifest, ChromePolicy, UiManifest
from runtimeV2.ui.startup_shutdown.startup import UIStartupResult
from runtimeV2.widgets.capabilities.widget_visibility_read import WidgetVisibilityRead
from runtimeV2.widgets.capabilities.widget_visibility_write import WidgetVisibilityWrite
from runtimeV2.widgets.capabilities.widget_records_read import WidgetRecordsRead
from runtimeV2.widgets.contracts import WidgetRecord, WidgetStatus
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
        if name == "connector_write":
            class _FakeConnectorWrite:
                def update(self, connector_id: str) -> bool:
                    return connector_id == "demo"

                def update_all(self) -> list[str]:
                    return ["demo"]

                def request_source(self, connector_id: str, owner: str, source_name: str) -> bool:
                    return True

                def release_source(self, connector_id: str, owner: str) -> bool:
                    return True

            return _FakeConnectorWrite()
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
        registry = EventRegistry()
        self._events = EventsStartupResult(
            bus=EventBus(),
            registry=registry,
            event_read=EventRead(registry),
            event_registration_write=None,
        )
        self._events = EventsStartupResult(
            bus=self._events.bus,
            registry=registry,
            event_read=self._events.event_read,
            event_registration_write=EventRegistrationWrite(registry, self._events.bus),
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
        self._widget_records_store = WidgetRecordsStore()
        self._widget_records = WidgetRecordsRead(self._widget_records_store)
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
        from runtimeV2.widgets.capabilities.widget_manual_override import WidgetManualOverride
        from runtimeV2.widgets.visibility_focus import WidgetVisibilityFocus
        self._widget_visibility_focus = WidgetVisibilityFocus()
        self._widget_visibility_read = WidgetVisibilityRead(
            WidgetConfigRead(widget_store),
            self._widget_visibility_focus,
        )
        self._widget_manual_override = WidgetManualOverride()
        widget_config_write = WidgetConfigWrite(widget_store)
        widget_config_write.set_global_widgets_visible(False)
        self._widget_visibility_write = WidgetVisibilityWrite(
            widget_config_write,
            self._widget_manual_override,
            focus=self._widget_visibility_focus,
        )
        self._plugin_active_calls: list[str] = []
        self._settings_save_all_calls = 0
        self._connector_source_requests: list[tuple[str, str, str]] = []
        self._connector_source_releases: list[tuple[str, str]] = []
        self._active_config_set = "default"
        self._plugin_panel_visible = False
        self._plugin_active_read = SimpleNamespace(get_active_plugin=lambda: "")

        class _FakePluginDiscovery:
            def plugin_ids(self) -> list[str]:
                return ["tinyui", "devtools"]

        class _FakePluginActiveWrite:
            def __init__(self, calls: list[str]) -> None:
                self._calls = calls

            def set_active_plugin(self, plugin_id: str) -> bool:
                self._calls.append(plugin_id)
                return True

        class _FakeConfigSetRead:
            def __init__(self, outer: "_FakeUiRuntime") -> None:
                self._outer = outer

            def list_sets(self) -> list[ConfigSet]:
                return [
                    ConfigSet(id="default", name="Default"),
                    ConfigSet(id="streaming", name="Streaming"),
                ]

        class _FakeConfigSetWrite:
            def __init__(self, outer: "_FakeUiRuntime") -> None:
                self._outer = outer

            def set_active(self, set_id: str) -> bool:
                self._outer._active_config_set = set_id
                return True

        class _FakeSettingsWrite:
            def __init__(self, outer: "_FakeUiRuntime") -> None:
                self._outer = outer

            def save_all(self) -> None:
                self._outer._settings_save_all_calls += 1

        class _FakePanelStateRead:
            def __init__(self, outer: "_FakeUiRuntime") -> None:
                self._outer = outer

            def plugin_panel_visible(self) -> bool:
                return self._outer._plugin_panel_visible

        class _FakePanelStateWrite:
            def __init__(self, outer: "_FakeUiRuntime") -> None:
                self._outer = outer

            def set_plugin_panel_visible(self, visible: bool) -> bool:
                changed = self._outer._plugin_panel_visible != visible
                self._outer._plugin_panel_visible = visible
                return changed

            def toggle_plugin_panel(self) -> bool:
                return self.set_plugin_panel_visible(not self._outer._plugin_panel_visible)

        class _FakeManifestConnectorRead:
            def connector_declarations(self) -> dict[str, ConnectorManifest]:
                return {
                    "LMU_RF2_Connector": ConnectorManifest(
                        runtime=ConnectorRuntimeDecl(mock_source="mock"),
                    ),
                    "no_mock_connector": ConnectorManifest(),
                }

        class _FakeConnectorWrite:
            def __init__(self, outer: "_FakeUiRuntime") -> None:
                self._outer = outer

            def request_source(self, connector_id: str, owner: str, source_name: str) -> bool:
                self._outer._connector_source_requests.append((connector_id, owner, source_name))
                return True

            def release_source(self, connector_id: str, owner: str) -> bool:
                self._outer._connector_source_releases.append((connector_id, owner))
                return True

        self._plugin_discovery = _FakePluginDiscovery()
        self._plugin_active_write = _FakePluginActiveWrite(self._plugin_active_calls)
        self._config_set_read = _FakeConfigSetRead(self)
        self._config_set_write = _FakeConfigSetWrite(self)
        self._settings_write = _FakeSettingsWrite(self)
        self._panel_state_read = _FakePanelStateRead(self)
        self._panel_state_write = _FakePanelStateWrite(self)
        self._manifest_connector_read = _FakeManifestConnectorRead()
        self._connector_write = _FakeConnectorWrite(self)
        self._globals = SimpleNamespace(
            read_global=lambda name, _capability_type: self._plugin_active_read
            if name == "active_plugin"
            else (_FakeShutdown(self._events) if name == "shutdown" else None),
            write_global=lambda name, _capability_type: self._plugin_active_write
            if name == "active_plugin"
            else (_FakeShutdown(self._events) if name == "shutdown" else None),
        )

    def domain_result(self, name: str, _result_type: type[Any]) -> Any:
        if name == "ui":
            return self._ui_result
        if name == "events":
            return self._events
        raise KeyError(name)

    def capability(self, name: str, _capability_type: type[Any]) -> Any:
        if name == "main_window_read":
            return self._main_window
        if name == "globals":
            return self._globals
        if name == "shutdown":
            return self.shutdown
        if name == "event_registration_write":
            return self._events.event_registration_write
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
        if name == "manifest_connector_read":
            return self._manifest_connector_read
        if name == "connector_write":
            return self._connector_write
        if name == "plugin_discovery":
            return self._plugin_discovery
        if name == "plugin_active_write":
            return self._plugin_active_write
        if name == "config_set_read":
            return self._config_set_read
        if name == "config_set_write":
            return self._config_set_write
        if name == "settings_write":
            return self._settings_write
        if name == "panel_state_read":
            return self._panel_state_read
        if name == "panel_state_write":
            return self._panel_state_write
        if name == "widget_visibility_read":
            return self._widget_visibility_read
        if name == "widget_visibility_write":
            return self._widget_visibility_write
        if name == "widget_manual_override":
            return self._widget_manual_override
        raise KeyError(name)


def _ui_host_registry(runtime: object) -> SharedRuntimeHostRegistry:
    registry = create_shared_runtime_host_registry(cast(Any, runtime))
    register_event_registration_host(registry)
    register_ui_runtime_host(registry)
    return registry


def test_bootv2_returns_zero_when_runtime_v2_is_render_ready(monkeypatch) -> None:
    """bootv2 should succeed once runtime V2 exposes a render-ready UI handoff."""

    app = _FakeApp()
    host_calls: list[str] = []

    def _startup_runtime_v2(*, host_bridge_startup) -> StartupResult:
        host_calls.append("runtime")
        return host_bridge_startup(object())

    monkeypatch.setattr(bootv2, "startup_runtime_v2", _startup_runtime_v2)
    monkeypatch.setattr(bootv2, "create_application", lambda: app)
    monkeypatch.setattr(bootv2, "create_engine", lambda: object())
    monkeypatch.setattr(
        bootv2,
        "startup_shared_runtime_host",
        lambda **_kwargs: (SimpleNamespace(), StartupResult(ok=True)),
    )

    assert bootv2.main() == 0
    assert app.exec_called
    assert host_calls == ["runtime"]


def test_bootv2_returns_error_when_runtime_v2_startup_fails(monkeypatch, capsys) -> None:
    """bootv2 should report startup failures from runtime V2."""

    monkeypatch.setattr(
        bootv2,
        "startup_runtime_v2",
        lambda **_kwargs: StartupResult(ok=False, error_message="broken"),
    )
    monkeypatch.setattr(bootv2, "create_application", lambda: _FakeApp())
    monkeypatch.setattr(bootv2, "create_engine", lambda: object())

    assert bootv2.main() == 1
    assert "broken" in capsys.readouterr().err


def test_bootv2_returns_error_when_shared_runtime_host_fails(monkeypatch, capsys) -> None:
    """bootv2 should report shared runtime host failures."""

    def _startup_runtime_v2(*, host_bridge_startup) -> StartupResult:
        return host_bridge_startup(object())

    monkeypatch.setattr(bootv2, "startup_runtime_v2", _startup_runtime_v2)
    monkeypatch.setattr(bootv2, "create_application", lambda: _FakeApp())
    monkeypatch.setattr(bootv2, "create_engine", lambda: object())
    monkeypatch.setattr(
        bootv2,
        "startup_shared_runtime_host",
        lambda **_kwargs: (None, StartupResult(ok=False, error_message="host bridge failed")),
    )

    assert bootv2.main() == 1
    assert "host bridge failed" in capsys.readouterr().err


def test_runtime_host_builds_qml_properties_from_ui_schema() -> None:
    """The ui_api host should apply the runtime V2 QML property schema."""

    runtime = _FakeCapabilityRuntime()
    ui_result = cast(Any, SimpleNamespace(qml_property_plan=[
        QmlPropertyPlan("manifest_read", "manifestRead"),
        QmlPropertyPlan("settings_read", "settingsRead"),
        QmlPropertyPlan("connector_write", "connectorActions"),
    ]))

    properties = build_runtime_qml_properties(
        cast(Any, runtime),
        cast(UIStartupResult, ui_result),
        create_shared_runtime_host_registry(cast(Any, runtime)),
    )

    assert isinstance(properties["manifestRead"], ManifestQmlCapability)
    assert isinstance(properties["settingsRead"], SettingsQmlCapability)
    assert isinstance(properties["connectorActions"], ConnectorWriteQmlCapability)
    assert runtime.calls == [
        ("manifest_read", "ManifestReader"),
        ("plugin_icon", "PluginIconResolver"),
        ("settings_read", "SettingsReader"),
        ("connector_write", "ConnectorWriter"),
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
        host_registry=_ui_host_registry(runtime),
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
        host_registry=_ui_host_registry(runtime),
    )

    assert startup_result.ok
    assert result is not None

    result.actions.trigger("open:devtools.main")

    assert opened == ["tinyui.main", "devtools.main"]
    assert "devtools.main" in result.window_handles


def test_runtime_host_shutdown_closes_secondary_windows(monkeypatch) -> None:
    """Runtime shutdown should close both the main window and opened secondary windows."""

    app = _FakeApp()
    runtime = _FakeUiRuntime()
    close_calls: list[str] = []

    class _FakeWindow:
        def __init__(self, window_id: str) -> None:
            self.window_id = window_id
            self.destroyed = _FakeSignal()

        def close(self) -> None:
            close_calls.append(self.window_id)

        def raise_(self) -> None:
            return None

        def requestActivate(self) -> None:
            return None

    def _open_window(manifest, *_args, **_kwargs):
        return SimpleNamespace(qml_window=_FakeWindow(manifest.id), keepalive=())

    monkeypatch.setattr("ui_api.runtime_host.open_window", _open_window)

    result, startup_result = start_runtime_host(
        app=app,
        engine=object(),
        runtime=cast(Any, runtime),
        host_registry=_ui_host_registry(runtime),
    )

    assert startup_result.ok
    assert result is not None

    result.actions.trigger("open:devtools.main")
    runtime.shutdown.begin_shutdown("main_window_close")

    assert close_calls == ["tinyui.main", "devtools.main"]


def test_runtime_host_secondary_window_close_does_not_request_runtime_shutdown(monkeypatch) -> None:
    """Closing a secondary host window should not trigger runtime shutdown."""

    app = _FakeApp()
    runtime = _FakeUiRuntime()
    opened_windows: dict[str, _FakeWindow] = {}

    class _FakeWindow:
        def __init__(self, window_id: str) -> None:
            self.window_id = window_id
            self.destroyed = _FakeSignal()
            self.closed = False
            self.properties: dict[str, object] = {}

        def close(self) -> None:
            self.closed = True

        def raise_(self) -> None:
            return None

        def requestActivate(self) -> None:
            return None

        def setProperty(self, key: str, value: object) -> None:
            self.properties[key] = value

    def _open_window(manifest, *_args, **kwargs):
        window = _FakeWindow(manifest.id)
        window.properties.update(kwargs)
        opened_windows[manifest.id] = window
        return SimpleNamespace(qml_window=window, keepalive=())

    monkeypatch.setattr("ui_api.runtime_host.open_window", _open_window)

    result, startup_result = start_runtime_host(
        app=app,
        engine=object(),
        runtime=cast(Any, runtime),
        host_registry=_ui_host_registry(runtime),
    )

    assert startup_result.ok
    assert result is not None

    result.actions.trigger("open:devtools.main")

    assert opened_windows["tinyui.main"].properties["isMainWindow"] is True
    assert opened_windows["devtools.main"].properties["isMainWindow"] is False

    opened_windows["devtools.main"].close()

    assert runtime.shutdown.calls == []


def test_runtime_host_reopens_secondary_window_after_close(monkeypatch) -> None:
    """Closed secondary windows should be recreated on the next open action."""

    app = _FakeApp()
    runtime = _FakeUiRuntime()
    opened: list[str] = []
    opened_windows: dict[str, _FakeWindow] = {}

    class _FakeWindow:
        def __init__(self, window_id: str) -> None:
            self.window_id = window_id
            self.destroyed = _FakeSignal()
            self._visible = True

        def close(self) -> None:
            self._visible = False

        def raise_(self) -> None:
            return None

        def requestActivate(self) -> None:
            return None

        def isVisible(self) -> bool:
            return self._visible

    def _open_window(manifest, *_args, **_kwargs):
        opened.append(manifest.id)
        window = _FakeWindow(manifest.id)
        opened_windows[manifest.id] = window
        return SimpleNamespace(qml_window=window, keepalive=())

    monkeypatch.setattr("ui_api.runtime_host.open_window", _open_window)

    result, startup_result = start_runtime_host(
        app=app,
        engine=object(),
        runtime=cast(Any, runtime),
        host_registry=_ui_host_registry(runtime),
    )

    assert startup_result.ok
    assert result is not None

    result.actions.trigger("open:devtools.main")
    opened_windows["devtools.main"].close()
    result.actions.trigger("open:devtools.main")

    assert opened == ["tinyui.main", "devtools.main", "devtools.main"]


def test_runtime_host_widget_visibility_toggle_uses_runtime_capability(monkeypatch) -> None:
    """The ui_api host should toggle widget visibility and manifest mock sources."""

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
        host_registry=_ui_host_registry(runtime),
    )

    assert startup_result.ok
    assert result is not None
    assert runtime._widget_visibility_read.global_visible() is False
    assert runtime._widget_manual_override.is_manually_enabled() is False
    assert runtime._connector_source_requests == []

    result.actions.trigger("widgetVisibility.toggle")

    assert runtime._widget_visibility_read.global_visible() is True
    assert runtime._widget_manual_override.is_manually_enabled() is True
    assert runtime._connector_source_requests == [
        ("LMU_RF2_Connector", "tinyui.statusbar.widgets", "mock"),
    ]
    assert runtime._connector_source_releases == []

    result.actions.trigger("widgetVisibility.toggle")

    assert runtime._widget_visibility_read.global_visible() is False
    assert runtime._widget_manual_override.is_manually_enabled() is False
    assert runtime._connector_source_releases == [
        ("LMU_RF2_Connector", "tinyui.statusbar.widgets"),
    ]


def test_runtime_host_exposes_widget_preview_actions_to_qml(monkeypatch) -> None:
    """The ui_api host should expose shared widget preview actions to tab surfaces."""

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
        host_registry=_ui_host_registry(runtime),
    )

    assert startup_result.ok
    assert result is not None
    preview_actions = result.qml_properties["widgetPreviewActions"]
    assert isinstance(preview_actions, WidgetPreviewActions)

    preview_actions.setPreviewVisible(True)

    assert runtime._widget_visibility_read.global_visible() is True
    assert runtime._connector_source_requests == [
        ("LMU_RF2_Connector", "tinyui.statusbar.widgets", "mock"),
    ]

    preview_actions.setPreviewVisible(False)

    assert runtime._widget_visibility_read.global_visible() is False
    assert runtime._connector_source_releases == [
        ("LMU_RF2_Connector", "tinyui.statusbar.widgets"),
    ]


def test_widget_preview_actions_can_focus_one_widget_before_mock_preview(monkeypatch) -> None:
    """Focused widget visibility should be independent from mock preview playback."""

    app = _FakeApp()
    runtime = _FakeUiRuntime()
    runtime._widget_records_store.set_records([
        WidgetRecord(
            overlay_id="demo_overlay",
            widget_id="speed",
            widget_type="text",
            label="Speed",
            source="speed",
            bindings={},
            status=WidgetStatus.READY,
            connector_ids=(),
        ),
        WidgetRecord(
            overlay_id="demo_overlay",
            widget_id="rpm",
            widget_type="text",
            label="RPM",
            source="rpm",
            bindings={},
            status=WidgetStatus.READY,
            connector_ids=(),
        ),
    ])

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
        host_registry=_ui_host_registry(runtime),
    )

    assert startup_result.ok
    assert result is not None
    preview_actions = cast(WidgetPreviewActions, result.qml_properties["widgetPreviewActions"])

    preview_actions.setFocusedWidgetVisible("demo_overlay", "speed", True)

    assert runtime._widget_visibility_read.global_visible() is True
    assert runtime._widget_visibility_read.is_widget_enabled("demo_overlay", "speed") is True
    assert runtime._widget_visibility_read.is_widget_enabled("demo_overlay", "rpm") is True
    assert runtime._widget_visibility_read.focused_widget() == ("demo_overlay", "speed")
    assert runtime._connector_source_requests == []

    preview_actions.setFocusedPreviewVisible("demo_overlay", "speed", True)

    assert runtime._connector_source_requests == [
        ("LMU_RF2_Connector", "tinyui.statusbar.widgets", "mock"),
    ]

    preview_actions.setFocusedPreviewVisible("demo_overlay", "speed", False)

    assert runtime._widget_visibility_read.global_visible() is True
    assert runtime._widget_visibility_read.is_widget_enabled("demo_overlay", "speed") is True
    assert runtime._widget_visibility_read.is_widget_enabled("demo_overlay", "rpm") is True
    assert runtime._widget_visibility_read.focused_widget() == ("demo_overlay", "speed")
    assert runtime._connector_source_releases == [
        ("LMU_RF2_Connector", "tinyui.statusbar.widgets"),
    ]

    preview_actions.setFocusedWidgetVisible("demo_overlay", "speed", False)

    assert runtime._widget_visibility_read.global_visible() is False
    assert runtime._widget_visibility_read.is_widget_enabled("demo_overlay", "speed") is True
    assert runtime._widget_visibility_read.is_widget_enabled("demo_overlay", "rpm") is True
    assert runtime._widget_visibility_read.focused_widget() is None


def test_runtime_host_plugin_activate_action_uses_runtime_capability(monkeypatch) -> None:
    """The ui_api host should activate plugins through runtime-owned actions."""

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
        host_registry=_ui_host_registry(runtime),
    )

    assert startup_result.ok
    assert result is not None

    result.actions.trigger("plugin.activate:devtools")

    assert runtime._plugin_active_calls == ["devtools"]


def test_runtime_host_settings_save_all_action_uses_runtime_capability(monkeypatch) -> None:
    """The ui_api host should save settings through runtime-owned actions."""

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
        host_registry=_ui_host_registry(runtime),
    )

    assert startup_result.ok
    assert result is not None

    result.actions.trigger("settings.saveAll")

    assert runtime._settings_save_all_calls == 1


def test_runtime_host_config_set_activate_action_uses_runtime_capability(monkeypatch) -> None:
    """The ui_api host should activate config sets through runtime-owned actions."""

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
        host_registry=_ui_host_registry(runtime),
    )

    assert startup_result.ok
    assert result is not None

    result.actions.trigger("configSet.activate:streaming")

    assert runtime._active_config_set == "streaming"


def test_runtime_host_plugin_panel_toggle_uses_runtime_capability(monkeypatch) -> None:
    """The ui_api host should toggle plugin panel visibility through runtime-owned state."""

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
        host_registry=_ui_host_registry(runtime),
    )

    assert startup_result.ok
    assert result is not None
    assert runtime._plugin_panel_visible is False

    result.actions.trigger("pluginPanel.toggle")

    assert runtime._plugin_panel_visible is True


def test_ui_startup_emits_window_record_change_before_ready(monkeypatch) -> None:
    """UI startup should emit a typed window-record update alongside readiness."""

    from runtimeV2.ui.startup_shutdown.startup import startup_ui

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
                "globals": cast(
                    Any,
                    SimpleNamespace(
                        read_global=lambda name, _capability_type: self.capabilities["plugin_active_read"]
                        if name == "active_plugin"
                        else None,
                    ),
                ),
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

    monkeypatch.setattr("runtimeV2.ui.startup_shutdown.startup.project_ui_window_records", lambda **_kwargs: [])
    monkeypatch.setattr(
        "runtimeV2.ui.startup_shutdown.startup.determine_render_status",
        lambda **_kwargs: UIRenderStatus(render_ready=True, main_window_id="tinyui.main"),
    )
    monkeypatch.setattr(
        "runtimeV2.ui.startup_shutdown.startup.build_ui_chrome_model",
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

