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

"""Connector read capability for runtime V2."""

from __future__ import annotations

from runtimeV2.connectors.contracts import ConnectorInspectionSnapshot, ConnectorServiceRecord
from runtimeV2.connectors.service_registry import ConnectorServiceRegistry


class ConnectorRead:
    """Read connector service registry state."""

    def __init__(self, registry: ConnectorServiceRegistry) -> None:
        self._registry = registry

    def services(self) -> list[ConnectorServiceRecord]:
        """Return active connector service records."""

        return self._registry.records()

    def ids(self) -> list[str]:
        """Return active connector ids."""

        return self._registry.ids()

    def has(self, connector_id: str) -> bool:
        """Return True when a connector is active."""

        return self._registry.has(connector_id)

    def service(self, connector_id: str) -> ConnectorServiceRecord | None:
        """Return one connector service record."""

        return self._registry.metadata(connector_id)

    def inspection_rows(self, connector_id: str) -> ConnectorInspectionSnapshot:
        """Return connector inspection rows."""

        return self._registry.inspect(connector_id)

    def inspection_map(self, connector_id: str) -> dict[str, str]:
        """Return one connector inspection snapshot keyed by name."""

        return dict(self.inspection_rows(connector_id))

    def value(self, connector_id: str, key: str) -> str | None:
        """Return one inspection value by key."""

        return self.inspection_map(connector_id).get(key)

    def active_source(self, connector_id: str) -> str | None:
        """Return the active source name for one connector service when available."""

        service = self._registry.get(connector_id)
        if service is None or not hasattr(service, "active_source"):
            return None
        return str(service.active_source())

    def active_game(self, connector_id: str) -> str | None:
        """Return the active game name for one connector service when available."""

        service = self._registry.get(connector_id)
        if service is None or not hasattr(service, "active_game"):
            return None
        return str(service.active_game())
