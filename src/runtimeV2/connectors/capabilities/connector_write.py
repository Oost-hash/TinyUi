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

"""Connector write capability for runtime V2."""

from __future__ import annotations

from runtimeV2.connectors.contracts import ConnectorSourceChangedData
from runtimeV2.events.contracts import EventBus, EventType
from runtimeV2.connectors.poller import ConnectorServicePoller
from runtimeV2.connectors.service_registry import ConnectorServiceRegistry


class ConnectorWrite:
    """Control connector service sources and updates."""

    def __init__(
        self,
        registry: ConnectorServiceRegistry,
        poller: ConnectorServicePoller,
        events: EventBus | None = None,
    ) -> None:
        self._registry = registry
        self._poller = poller
        self._events = events

    def request_source(self, connector_id: str, owner: str, source_name: str) -> bool:
        """Request a connector source."""

        changed = self._registry.request_source(connector_id, owner, source_name)
        if changed:
            self._emit_source_changed(
                connector_id=connector_id,
                owner=owner,
                source_name=source_name,
                action="request",
            )
        return changed

    def release_source(self, connector_id: str, owner: str) -> bool:
        """Release a connector source claim."""

        changed = self._registry.release_source(connector_id, owner)
        if changed:
            self._emit_source_changed(
                connector_id=connector_id,
                owner=owner,
                source_name="",
                action="release",
            )
        return changed

    def update(self, connector_id: str) -> bool:
        """Update one connector service."""

        return self._poller.update_one(connector_id)

    def update_all(self) -> list[str]:
        """Update all connector services."""

        return self._poller.update_all()

    def _emit_source_changed(
        self,
        *,
        connector_id: str,
        owner: str,
        source_name: str,
        action: str,
    ) -> None:
        if self._events is None:
            return
        self._events.emit_typed(
            EventType.CONNECTOR_SOURCE_CHANGED,
            ConnectorSourceChangedData(
                connector_id=connector_id,
                plugin_id=connector_id,
                owner=owner,
                source_name=source_name,
                action=action,
            ),
            source="connectors",
        )
