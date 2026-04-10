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

"""Connector polling/update helpers for runtime V2."""

from __future__ import annotations

from runtimeV2.contracts import ConnectorServiceUpdatedData
from runtimeV2.connectors.service_registry import ConnectorServiceRegistry
from runtimeV2.contracts import EventBus, EventType


class ConnectorServicePoller:
    """Advance connector services and emit update events."""

    def __init__(self, registry: ConnectorServiceRegistry, events: EventBus | None = None) -> None:
        self._registry = registry
        self._events = events

    def update_one(self, connector_id: str) -> bool:
        """Update one connector service."""

        if not self._registry.update(connector_id):
            return False
        self._emit_updated(connector_id)
        return True

    def update_all(self) -> list[str]:
        """Update all active connector services."""

        updated: list[str] = []
        for connector_id in self._registry.ids():
            if self._registry.update(connector_id):
                updated.append(connector_id)
                self._emit_updated(connector_id)
        return updated

    def _emit_updated(self, connector_id: str) -> None:
        if self._events is None:
            return
        self._events.emit_typed(
            EventType.CONNECTOR_SERVICE_UPDATED,
            ConnectorServiceUpdatedData(
                connector_id=connector_id,
                plugin_id=connector_id,
            ),
            source="connectors",
        )
