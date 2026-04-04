"""Connector actions capability."""

from __future__ import annotations

from PySide6.QtCore import QObject, Signal, Slot

from runtime.connectors.service_registry import ConnectorServiceRegistry


class ConnectorActions(QObject):
    """Expose connector service operational actions to QML consumers."""

    connectorDataChanged = Signal(str)

    def __init__(self, connector_services: ConnectorServiceRegistry, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._connector_services = connector_services

    @Slot(str, str, str, result=bool)
    def requestSource(self, connector_id: str, owner: str, source_name: str) -> bool:
        result = self._connector_services.request_source(connector_id, owner, source_name)
        if result:
            self.connectorDataChanged.emit(connector_id)
        return result

    @Slot(str, str, result=bool)
    def releaseSource(self, connector_id: str, owner: str) -> bool:
        result = self._connector_services.release_source(connector_id, owner)
        if result:
            self.connectorDataChanged.emit(connector_id)
        return result

    @Slot(str, result=bool)
    def updateConnector(self, connector_id: str) -> bool:
        result = self._connector_services.update(connector_id)
        if result:
            self.connectorDataChanged.emit(connector_id)
        return result
