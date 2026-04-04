"""Connector read capability."""

from __future__ import annotations

from PySide6.QtCore import Property, QObject, Signal, Slot

from runtime.connectors.service_registry import ConnectorServiceRegistry
from runtime_schema import (
    ConnectorServiceRegisteredData,
    ConnectorServiceUnregisteredData,
    ConnectorServiceUpdatedData,
    EventBus,
    EventType,
)


class ConnectorRead(QObject):
    """Expose active connector services and snapshots to QML consumers."""

    servicesChanged = Signal()
    connectorDataChanged = Signal(str)

    def __init__(
        self,
        event_bus: EventBus,
        connector_services: ConnectorServiceRegistry,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._event_bus = event_bus
        self._connector_services = connector_services
        self._connector_labels: dict[str, str] = {}
        self._connector_plugins: dict[str, str] = {}
        self._subscribe()

    def _subscribe(self) -> None:
        self._event_bus.on(
            EventType.CONNECTOR_SERVICE_REGISTERED,
            self._on_connector_service_registered,
            replay_history=True,
        )
        self._event_bus.on(
            EventType.CONNECTOR_SERVICE_UNREGISTERED,
            self._on_connector_service_unregistered,
            replay_history=True,
        )
        self._event_bus.on(EventType.CONNECTOR_SERVICE_UPDATED, self._on_connector_service_updated)

    def _on_connector_service_registered(self, event) -> None:
        data = event.data
        if isinstance(data, ConnectorServiceRegisteredData):
            self._connector_labels[data.connector_id] = data.display_name or data.connector_id
            self._connector_plugins[data.connector_id] = data.plugin_id
            self.servicesChanged.emit()
            self.connectorDataChanged.emit(data.connector_id)

    def _on_connector_service_unregistered(self, event) -> None:
        data = event.data
        if isinstance(data, ConnectorServiceUnregisteredData):
            self._connector_labels.pop(data.connector_id, None)
            self._connector_plugins.pop(data.connector_id, None)
            self.servicesChanged.emit()
            self.connectorDataChanged.emit(data.connector_id)

    def _on_connector_service_updated(self, event) -> None:
        data = event.data
        if isinstance(data, ConnectorServiceUpdatedData):
            self.connectorDataChanged.emit(data.connector_id)

    @Property(list, notify=servicesChanged)
    def services(self) -> list[dict]:
        return [
            {
                "id": connector_id,
                "label": self._connector_labels.get(connector_id, connector_id),
                "pluginId": self._connector_plugins.get(connector_id, ""),
            }
            for connector_id in self._connector_services.ids()
        ]

    @Slot(str, result=list)
    def inspectionRows(self, connector_id: str) -> list[dict]:
        return [{"key": key, "value": value} for key, value in self._connector_services.inspect(connector_id)]
