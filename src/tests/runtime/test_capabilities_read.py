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
from runtime.plugins.plugin_state import PluginStateMachine
from runtime.providers.provider_registry import ProviderRegistry
from runtime_schema import (
    EventBus,
    EventType,
    MenuRegisteredData,
    PluginActivatedData,
    PluginErrorData,
    PluginState,
    PluginStateData,
    ProviderRegisteredData,
    ProviderUnregisteredData,
    ProviderUpdatedData,
    StatusbarRegisteredData,
    TabRegisteredData,
)


class _FakeProvider:
    def inspect_snapshot(self) -> list[tuple[str, str]]:
        return [("provider.mode", "demo"), ("provider.active_source", "mock")]


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
                windows=[SimpleNamespace(id="tinyui.main")],
                settings=[],
            ),
            "dummy_plugin": SimpleNamespace(
                plugin_type="plugin",
                version="1.0.0",
                author="Test",
                description="Dummy",
                requires=["telemetry_connector"],
                windows=[SimpleNamespace(id="dummy.main")],
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

    def plugin_ids(self) -> list[str]:
        return list(self._plugin_manifests.keys())

    def plugin_manifest(self, plugin_id: str):
        return self._plugin_manifests.get(plugin_id)

    def plugin_icon_url(self, plugin_id: str) -> str:
        return self._icon_urls[plugin_id]

    def get_plugin_state_machine(self, plugin_id: str):
        return self._state_machines.get(plugin_id)


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


def test_connector_read_projects_provider_metadata_and_rows() -> None:
    """ConnectorRead should expose active providers and snapshot rows."""
    bus = EventBus()
    registry = ProviderRegistry()
    registry.register("telemetry_connector", "telemetry_connector", "Telemetry", _FakeProvider())
    capability = ConnectorRead(bus, registry)

    bus.emit_typed(
        EventType.PROVIDER_REGISTERED,
        ProviderRegisteredData(
            provider_id="telemetry_connector",
            plugin_id="telemetry_connector",
            display_name="Telemetry",
        ),
    )
    bus.emit_typed(
        EventType.PROVIDER_UPDATED,
        ProviderUpdatedData(provider_id="telemetry_connector", plugin_id="telemetry_connector"),
    )

    assert cast(list[dict[str, str]], cast(Any, capability).providers) == [
        {"id": "telemetry_connector", "label": "Telemetry", "pluginId": "telemetry_connector"}
    ]
    assert capability.inspectionRows("telemetry_connector") == [
        {"key": "provider.mode", "value": "demo"},
        {"key": "provider.active_source", "value": "mock"},
    ]

    bus.emit_typed(
        EventType.PROVIDER_UNREGISTERED,
        ProviderUnregisteredData(provider_id="telemetry_connector", plugin_id="telemetry_connector"),
    )
    registry.unregister("telemetry_connector")

    assert cast(list[dict[str, str]], cast(Any, capability).providers) == []
