"""Unit tests for write-side runtime capabilities."""

from __future__ import annotations

from typing import Any, cast

from capabilities.connector_actions import ConnectorActions
from capabilities.plugin_selection import PluginSelectionActions
from capabilities.plugin_state_write import PluginStateWrite
from capabilities.settings_write import SettingsWrite
from runtime.connectors.service_registry import ConnectorServiceRegistry
from runtime_schema import EventBus, EventType


class _FakeConnectorService:
    def __init__(self) -> None:
        self.requests: list[tuple[str, str]] = []
        self.releases: list[str] = []
        self.updated = 0

    def request_source(self, owner: str, source_name: str) -> bool:
        self.requests.append((owner, source_name))
        return True

    def release_source(self, owner: str) -> bool:
        self.releases.append(owner)
        return True

    def update(self) -> None:
        self.updated += 1


class _FakeSettingsRegistry:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str, object]] = []
        self.saved_namespaces: list[str] = []

    def set(self, namespace: str, key: str, value: object) -> None:
        self.calls.append((namespace, key, value))

    def save(self, namespace: str) -> None:
        self.saved_namespaces.append(namespace)


class _FakeSettingsRead:
    def __init__(self) -> None:
        self.refresh_calls = 0

    def refresh(self) -> None:
        self.refresh_calls += 1


class _FakeRuntime:
    def __init__(self) -> None:
        self.enabled: list[str] = []
        self.disabled: list[str] = []
        self.settings = _FakeSettingsRegistry()

    def enable_plugin(self, plugin_id: str) -> bool:
        self.enabled.append(plugin_id)
        return True

    def disable_plugin(self, plugin_id: str) -> bool:
        self.disabled.append(plugin_id)
        return True


def test_plugin_selection_actions_emits_ui_plugin_selected_event() -> None:
    """PluginSelectionActions should emit a UI selection request onto the event bus."""
    bus = EventBus()
    received: list[str] = []
    bus.on(EventType.UI_PLUGIN_SELECTED, lambda event: received.append(event.data.plugin_id))
    capability = PluginSelectionActions(bus)

    result = capability.setActivePlugin("dummy_plugin")

    assert result is True
    assert received == ["dummy_plugin"]


def test_plugin_state_write_delegates_to_runtime() -> None:
    """PluginStateWrite should call runtime lifecycle methods directly."""
    runtime = _FakeRuntime()
    capability = PluginStateWrite(cast(Any, runtime))

    assert capability.enablePlugin("dummy_plugin") is True
    assert capability.disablePlugin("dummy_plugin") is True
    assert runtime.enabled == ["dummy_plugin"]
    assert runtime.disabled == ["dummy_plugin"]


def test_settings_write_persists_namespace_and_refreshes_read_model() -> None:
    """SettingsWrite should save the namespace and refresh the paired read model."""
    runtime = _FakeRuntime()
    settings_read = _FakeSettingsRead()
    capability = SettingsWrite(cast(Any, runtime), settings_read)

    result = capability.setString("dummy_plugin", "theme", "light")

    assert result is True
    assert runtime.settings.calls == [("dummy_plugin", "theme", "light")]
    assert runtime.settings.saved_namespaces == ["dummy_plugin"]
    assert settings_read.refresh_calls == 1


def test_connector_actions_delegate_to_registry_and_emit_on_success() -> None:
    """ConnectorActions should forward operational actions and emit change notifications."""
    registry = ConnectorServiceRegistry()
    service = _FakeConnectorService()
    registry.register("telemetry_connector", "telemetry_connector", "Telemetry", service)
    capability = ConnectorActions(registry)
    changed: list[str] = []
    capability.connectorDataChanged.connect(changed.append)

    assert capability.requestSource("telemetry_connector", "devtools", "mock") is True
    assert capability.releaseSource("telemetry_connector", "devtools") is True
    assert capability.updateConnector("telemetry_connector") is True

    assert service.requests == [("devtools", "mock")]
    assert service.releases == ["devtools"]
    assert service.updated == 1
    assert changed == ["telemetry_connector", "telemetry_connector", "telemetry_connector"]


def test_connector_actions_return_false_when_connector_is_missing() -> None:
    """ConnectorActions should fail cleanly for unknown connectors."""
    capability = ConnectorActions(ConnectorServiceRegistry())

    assert capability.requestSource("missing", "devtools", "mock") is False
    assert capability.releaseSource("missing", "devtools") is False
    assert capability.updateConnector("missing") is False
