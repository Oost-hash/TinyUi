#  TinyUI
#  Copyright (C) 2026 Oost-hash
#
#  This file is part of TinyUI.
#
#  TinyUI is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  TinyUI is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#  TinyUI builds on TinyPedal by s-victor (https://github.com/s-victor/TinyPedal),
#  licensed under GPLv3.

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
