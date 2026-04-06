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

"""Runtime registry for active connector services."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from runtime.connectors.contracts import ConnectorInspectionSnapshot, ConnectorServiceAccess


def _empty_snapshot() -> ConnectorInspectionSnapshot:
    return []


@dataclass
class RegisteredConnectorService:
    """Connector service instance and metadata."""

    connector_id: str
    plugin_id: str
    display_name: str
    instance: Any


class ConnectorServiceRegistry(ConnectorServiceAccess):
    """Stores active connector services and exposes common control operations."""

    def __init__(self) -> None:
        self._services: dict[str, RegisteredConnectorService] = {}

    def register(self, connector_id: str, plugin_id: str, display_name: str, instance: Any) -> None:
        self._services[connector_id] = RegisteredConnectorService(
            connector_id=connector_id,
            plugin_id=plugin_id,
            display_name=display_name,
            instance=instance,
        )

    def unregister(self, connector_id: str) -> bool:
        return self._services.pop(connector_id, None) is not None

    def has(self, connector_id: str) -> bool:
        return connector_id in self._services

    def get(self, connector_id: str) -> Any | None:
        service = self._services.get(connector_id)
        return service.instance if service else None

    def metadata(self, connector_id: str) -> RegisteredConnectorService | None:
        return self._services.get(connector_id)

    def ids(self) -> list[str]:
        return list(self._services.keys())

    def inspect(self, connector_id: str) -> ConnectorInspectionSnapshot:
        service = self.get(connector_id)
        if service is None or not hasattr(service, "inspect_snapshot"):
            return _empty_snapshot()
        snapshot = service.inspect_snapshot()
        return list(snapshot) if isinstance(snapshot, list) else _empty_snapshot()

    def request_source(self, connector_id: str, owner: str, source_name: str) -> bool:
        service = self.get(connector_id)
        if service is None or not hasattr(service, "request_source"):
            return False
        return bool(service.request_source(owner, source_name))

    def release_source(self, connector_id: str, owner: str) -> bool:
        service = self.get(connector_id)
        if service is None or not hasattr(service, "release_source"):
            return False
        return bool(service.release_source(owner))

    def update(self, connector_id: str) -> bool:
        service = self.get(connector_id)
        if service is None or not hasattr(service, "update"):
            return False
        service.update()
        return True
