"""Unit tests for read-side runtime capabilities."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any, cast

from capabilities.connector_read import ConnectorRead
from capabilities.menu import MenuApi
from capabilities.plugin_read import PluginRead
from capabilities.plugin_selection import PluginSelectionApi
from capabilities.plugin_state_read import PluginStateRead
from capabilities.settings_read import SettingsRead
from capabilities.statusbar import StatusbarApi
from capabilities.tabs import TabsApi
from capabilities.window_read import WindowRead
from capabilities.widget_read import WidgetRead
from runtime.ui import WindowRuntimeRecord, WindowRuntimeStatus as WindowStatus
from runtime.connectors.service_registry import ConnectorServiceRegistry
from runtime.plugins.plugin_state import PluginStateMachine
from runtime.widgets import WidgetRuntimeRecord, WidgetRuntimeStatus
from runtime_schema import (
    ConnectorServiceRegisteredData,
    ConnectorServiceUnregisteredData,
    ConnectorServiceUpdatedData,
    EventBus,
    EventType,
    MenuRegisteredData,
    PluginActivatedData,
    PluginErrorData,
    PluginState,
    PluginStateData,
    StatusbarRegisteredData,
    TabRegisteredData,
    RuntimeShutdownData,
    WindowRuntimeUpdatedData,
    WidgetRuntimeUpdatedData,
)


class _FakeConnectorService:
    def inspect_snapshot(self) -> list[tuple[str, str]]:
        return [("connector.mode", "demo"), ("connector.active_source", "mock")]


class _FakeSettingsRegistry:
    def __init__(self) -> None:
        self._specs = {
            "dummy_plugin": [
                SimpleNamespace(key="theme", type="choice", default="dark"),
                SimpleNamespace(key="enabled", type="bool", default=True),
            ]
        }
        self._values = {
            ("dummy_plugin", "theme"): "light",
            ("dummy_plugin", "enabled"): False,
        }

    def by_namespace(self) -> dict[str, list[object]]:
        return cast(dict[str, list[object]], self._specs)

    def get(self, namespace: str, key: str) -> Any:
        return self._values.get((namespace, key))


class _FakeRuntimeForRead:
    def __init__(self) -> None:
        self.settings = _FakeSettingsRegistry()
        self._plugin_manifests = {
            "tinyui": SimpleNamespace(
                plugin_type="host",
                version="0.5.0",
                author="Oost-hash",
                description="Host",
                requires=[],
                ui=SimpleNamespace(windows=[SimpleNamespace(id="tinyui.main")]),
                settings=[],
            ),
            "dummy_plugin": SimpleNamespace(
                plugin_type="plugin",
                version="1.0.0",
                author="Test",
                description="Dummy",
                requires=["telemetry_connector"],
                ui=SimpleNamespace(windows=[SimpleNamespace(id="dummy.main")]),
                settings=[object(), object()],
            ),
        }
        self._icon_urls = {
            "tinyui": "file:///host/logo.png",
            "dummy_plugin": "file:///plugins/dummy/logo.png",
        }
        self._state_machines = {
            "dummy_plugin": PluginStateMachine("dummy_plugin"),
            "telemetry_connector": PluginStateMachine("telemetry_connector"),
        }
        self._state_machines["dummy_plugin"].transition(PluginState.ENABLING, "boot")
        self._state_machines["dummy_plugin"].transition(PluginState.LOADING, "boot")
        self._state_machines["dummy_plugin"].transition(PluginState.ACTIVE, "boot")
        self._widget_records = [
            WidgetRuntimeRecord(
                overlay_id="demo_overlay",
                widget_id="session_time_left",
                widget_type="textWidget",
                label="Session Time Left",
                source="session.time_left",
                status=WidgetRuntimeStatus.WAITING_FOR_GAME,
                connector_ids=("LMU_RF2_Connector",),
            )
        ]
        self._window_records = [
            WindowRuntimeRecord(
                window_id="tinyui.main",
                plugin_id="tinyui",
                window_role="main",
                status=WindowStatus.OPEN,
                visible=True,
                surface="C:/tinyui/surface.qml",
            )
        ]

    def plugin_ids(self) -> list[str]:
        return list(self._plugin_manifests.keys())

    def plugin_manifest(self, plugin_id: str):
        return self._plugin_manifests.get(plugin_id)

    def plugin_icon_url(self, plugin_id: str) -> str:
        return self._icon_urls[plugin_id]

    def get_plugin_state_machine(self, plugin_id: str):
        return self._state_machines.get(plugin_id)

    def active_overlay_widget_records(self) -> list[WidgetRuntimeRecord]:
        return list(self._widget_records)

    def window_records(self) -> list[WindowRuntimeRecord]:
        return list(self._window_records)


def test_plugin_read_projects_runtime_metadata() -> None:
    """PluginRead should expose canonical plugin metadata from runtime."""
    capability = PluginRead(cast(Any, _FakeRuntimeForRead()))

    items = capability.items()

    assert [item["id"] for item in items] == ["tinyui", "dummy_plugin"]
    assert items[1]["requires"] == ["telemetry_connector"]
    assert items[1]["windowCount"] == 1
    assert items[1]["settingCount"] == 2
    assert items[1]["iconUrl"] == "file:///plugins/dummy/logo.png"


def test_settings_read_projects_namespace_and_current_values() -> None:
    """SettingsRead should flatten registry data into QML-friendly rows."""
    capability = SettingsRead(cast(Any, _FakeRuntimeForRead()))

    settings = cast(list[dict[str, str]], cast(Any, capability).settings)

    assert settings == [
        {
            "namespace": "dummy_plugin",
            "key": "theme",
            "type": "choice",
            "currentValue": "light",
        },
        {
            "namespace": "dummy_plugin",
            "key": "enabled",
            "type": "bool",
            "currentValue": "False",
        },
    ]


def test_plugin_selection_api_tracks_activated_plugin() -> None:
    """PluginSelectionApi should mirror PLUGIN_ACTIVATED events."""
    bus = EventBus()
    capability = PluginSelectionApi(bus)

    bus.emit_typed(EventType.PLUGIN_ACTIVATED, PluginActivatedData(plugin_id="dummy_plugin"))

    assert capability.activePlugin == "dummy_plugin"


def test_menu_api_separates_host_menu_and_active_plugin_menu() -> None:
    """MenuApi should keep host menu and plugin menu contributions distinct."""
    bus = EventBus()
    capability = MenuApi(bus)

    bus.emit_typed(
        EventType.MENU_REGISTERED,
        MenuRegisteredData(window_id="tinyui.main", label="Settings", action="open:settings.main", source="host"),
    )
    bus.emit_typed(
        EventType.MENU_REGISTERED,
        MenuRegisteredData(window_id="plugin:dummy_plugin", label="Refresh", action="refresh", source="plugin"),
    )
    bus.emit_typed(EventType.PLUGIN_ACTIVATED, PluginActivatedData(plugin_id="dummy_plugin"))

    assert capability.menuItems == [{"label": "Settings", "action": "open:settings.main"}]
    assert capability.pluginMenuItems == [{"label": "Refresh", "action": "refresh"}]
    assert capability.pluginMenuLabel == "Dummy Plugin"


def test_statusbar_api_splits_left_and_right_items() -> None:
    """StatusbarApi should route contributions by side."""
    bus = EventBus()
    capability = StatusbarApi(bus)

    bus.emit_typed(
        EventType.STATUSBAR_REGISTERED,
        StatusbarRegisteredData(window_id="tinyui.main", text="Left", side="left", action="open:left"),
    )
    bus.emit_typed(
        EventType.STATUSBAR_REGISTERED,
        StatusbarRegisteredData(window_id="tinyui.main", text="Right", side="right", action="open:right"),
    )

    assert capability.leftItems == [{"icon": "", "text": "Left", "tooltip": "", "action": "open:left"}]
    assert capability.rightItems == [{"icon": "", "text": "Right", "tooltip": "", "action": "open:right"}]


def test_tabs_api_filters_to_host_and_active_plugin_tabs() -> None:
    """TabsApi should always keep host tabs and only expose the active plugin tabs."""
    bus = EventBus()
    capability = TabsApi(bus)

    bus.emit_typed(
        EventType.TAB_REGISTERED,
        TabRegisteredData(
            window_id="tinyui.main",
            id="tinyui.widgets",
            label="Widgets",
            target="tinyui.main",
            surface="C:\\tabs\\widgets.qml",
            plugin_id="tinyui",
        ),
    )
    bus.emit_typed(
        EventType.TAB_REGISTERED,
        TabRegisteredData(
            window_id="tinyui.main",
            id="dummy_plugin.main",
            label="Dummy",
            target="tinyui.main",
            surface="/tabs/dummy.qml",
            plugin_id="dummy_plugin",
        ),
    )
    bus.emit_typed(
        EventType.TAB_REGISTERED,
        TabRegisteredData(
            window_id="tinyui.main",
            id="other_plugin.main",
            label="Other",
            target="tinyui.main",
            surface="file:///tabs/other.qml",
            plugin_id="other_plugin",
        ),
    )
    bus.emit_typed(EventType.PLUGIN_ACTIVATED, PluginActivatedData(plugin_id="dummy_plugin"))

    model = cast(list[dict[str, str]], cast(Any, capability).tabModel)

    assert [item["id"] for item in model] == ["tinyui.widgets", "dummy_plugin.main"]
    assert model[0]["surface"].startswith("file:///")
    assert model[1]["surface"] == "file:///tabs/dummy.qml"


def test_plugin_state_read_tracks_states_errors_and_history() -> None:
    """PluginStateRead should rebuild state, errors and transition history from runtime and events."""
    runtime = _FakeRuntimeForRead()
    bus = EventBus()
    capability = PluginStateRead(cast(Any, runtime), bus)

    state_machine = runtime.get_plugin_state_machine("dummy_plugin")
    assert state_machine is not None
    state_machine.transition(PluginState.UNLOADING, "failing")
    state_machine.set_error("boom")
    bus.emit_typed(
        EventType.PLUGIN_STATE_CHANGED,
        PluginStateData(plugin_id="dummy_plugin", old_state="active", new_state="error"),
    )
    bus.emit_typed(
        EventType.PLUGIN_ERROR,
        PluginErrorData(plugin_id="dummy_plugin", error_message="boom"),
    )

    states = cast(dict[str, str], cast(Any, capability).states)
    errors = cast(dict[str, str], cast(Any, capability).errors)
    histories = cast(dict[str, list[dict[str, object]]], cast(Any, capability).histories)

    assert states["dummy_plugin"] == "error"
    assert errors["dummy_plugin"] == "boom"
    assert histories["dummy_plugin"][-1]["to"] == "error"


def test_connector_read_projects_service_metadata_and_rows() -> None:
    """ConnectorRead should expose active connector services and snapshot rows."""
    bus = EventBus()
    registry = ConnectorServiceRegistry()
    registry.register("telemetry_connector", "telemetry_connector", "Telemetry", _FakeConnectorService())
    capability = ConnectorRead(bus, registry)

    bus.emit_typed(
        EventType.CONNECTOR_SERVICE_REGISTERED,
        ConnectorServiceRegisteredData(
            connector_id="telemetry_connector",
            plugin_id="telemetry_connector",
            display_name="Telemetry",
        ),
    )
    bus.emit_typed(
        EventType.CONNECTOR_SERVICE_UPDATED,
        ConnectorServiceUpdatedData(connector_id="telemetry_connector", plugin_id="telemetry_connector"),
    )

    assert cast(list[dict[str, str]], cast(Any, capability).services) == [
        {"id": "telemetry_connector", "label": "Telemetry", "pluginId": "telemetry_connector"}
    ]
    assert capability.inspectionRows("telemetry_connector") == [
        {"key": "connector.mode", "value": "demo"},
        {"key": "connector.active_source", "value": "mock"},
    ]

    bus.emit_typed(
        EventType.CONNECTOR_SERVICE_UNREGISTERED,
        ConnectorServiceUnregisteredData(connector_id="telemetry_connector", plugin_id="telemetry_connector"),
    )
    registry.unregister("telemetry_connector")

    assert cast(list[dict[str, str]], cast(Any, capability).services) == []


def test_widget_read_projects_runtime_widget_records() -> None:
    """WidgetRead should expose active widget runtime records to QML consumers."""
    runtime = _FakeRuntimeForRead()
    bus = EventBus()
    capability = WidgetRead(cast(Any, runtime), bus)

    widgets = capability.items()

    assert widgets == [
        {
            "overlayId": "demo_overlay",
            "widgetId": "session_time_left",
            "widgetType": "textWidget",
            "label": "Session Time Left",
            "source": "session.time_left",
            "status": "waiting_for_game",
            "connectorIds": ["LMU_RF2_Connector"],
            "errorMessage": "",
        }
    ]


def test_widget_read_refreshes_on_runtime_events() -> None:
    """WidgetRead should rebuild its rows when runtime events change widget state."""
    runtime = _FakeRuntimeForRead()
    bus = EventBus()
    capability = WidgetRead(cast(Any, runtime), bus)

    runtime._widget_records = [
        WidgetRuntimeRecord(
            overlay_id="demo_overlay",
            widget_id="session_time_left",
            widget_type="textWidget",
            label="Session Time Left",
            source="session.time_left",
            status=WidgetRuntimeStatus.READY,
            connector_ids=("LMU_RF2_Connector",),
        )
    ]
    bus.emit_typed(
        EventType.CONNECTOR_SERVICE_UPDATED,
        ConnectorServiceUpdatedData(connector_id="LMU_RF2_Connector", plugin_id="LMU_RF2_Connector"),
    )

    widgets = capability.items()

    assert widgets[0]["status"] == "ready"


def test_widget_read_refreshes_on_widget_runtime_poll_event() -> None:
    """WidgetRead should refresh when the widget runtime poller publishes an update."""
    runtime = _FakeRuntimeForRead()
    bus = EventBus()
    capability = WidgetRead(cast(Any, runtime), bus)

    runtime._widget_records = [
        WidgetRuntimeRecord(
            overlay_id="demo_overlay",
            widget_id="session_time_left",
            widget_type="textWidget",
            label="Session Time Left",
            source="session.time_left",
            status=WidgetRuntimeStatus.READY,
            connector_ids=("LMU_RF2_Connector",),
        )
    ]
    bus.emit_typed(
        EventType.WIDGET_RUNTIME_UPDATED,
        WidgetRuntimeUpdatedData(reason="game_detection_poll"),
    )

    widgets = capability.items()

    assert widgets[0]["status"] == "ready"


def test_widget_read_clears_rows_on_runtime_shutdown() -> None:
    """WidgetRead should clear active widget rows when runtime shutdown starts."""
    runtime = _FakeRuntimeForRead()
    bus = EventBus()
    capability = WidgetRead(cast(Any, runtime), bus)

    runtime._widget_records = []
    bus.emit_typed(
        EventType.RUNTIME_SHUTDOWN,
        RuntimeShutdownData(reason="app_quit"),
    )

    assert capability.items() == []


def test_window_read_projects_runtime_window_records() -> None:
    """WindowRead should expose runtime-owned window records to QML consumers."""
    runtime = _FakeRuntimeForRead()
    bus = EventBus()
    capability = WindowRead(cast(Any, runtime), bus)

    assert capability.items() == [
        {
            "windowId": "tinyui.main",
            "pluginId": "tinyui",
            "windowRole": "main",
            "status": "open",
            "visible": True,
            "surface": "C:/tinyui/surface.qml",
            "errorMessage": "",
        }
    ]


def test_window_read_refreshes_on_window_runtime_event() -> None:
    """WindowRead should rebuild rows when window runtime events fire."""
    runtime = _FakeRuntimeForRead()
    bus = EventBus()
    capability = WindowRead(cast(Any, runtime), bus)

    runtime._window_records = [
        WindowRuntimeRecord(
            window_id="tinyui.main",
            plugin_id="tinyui",
            window_role="main",
            status=WindowStatus.CLOSING,
            visible=False,
            surface="C:/tinyui/surface.qml",
        )
    ]
    bus.emit_typed(
        EventType.WINDOW_RUNTIME_UPDATED,
        WindowRuntimeUpdatedData(reason="shutdown"),
    )

    items = capability.items()

    assert items[0]["status"] == "closing"
    assert items[0]["visible"] is False
