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

"""Connector service registry for runtime V2."""

from __future__ import annotations

from typing import Any

from runtimeV2.contracts import ConnectorInspectionSnapshot, ConnectorServiceRecord


def _empty_snapshot() -> ConnectorInspectionSnapshot:
    return []


class ConnectorServiceRegistry:
    """Stores active connector services and exposes control operations."""

    def __init__(self) -> None:
        self._services: dict[str, ConnectorServiceRecord] = {}
        self._source_requests: dict[str, dict[str, str]] = {}

    def register(self, connector_id: str, plugin_id: str, display_name: str, instance: Any) -> None:
        """Register one connector service instance."""

        self._services[connector_id] = ConnectorServiceRecord(
            connector_id=connector_id,
            plugin_id=plugin_id,
            display_name=display_name,
            instance=instance,
        )

    def unregister(self, connector_id: str) -> bool:
        """Unregister one connector service."""

        removed = self._services.pop(connector_id, None) is not None
        if removed:
            self._source_requests.pop(connector_id, None)
        return removed

    def has(self, connector_id: str) -> bool:
        """Return True when a connector service is active."""

        return connector_id in self._services

    def get(self, connector_id: str) -> Any | None:
        """Return one raw connector service instance."""

        service = self._services.get(connector_id)
        return None if service is None else service.instance

    def metadata(self, connector_id: str) -> ConnectorServiceRecord | None:
        """Return one service metadata record."""

        return self._services.get(connector_id)

    def records(self) -> list[ConnectorServiceRecord]:
        """Return all active service metadata records."""

        return list(self._services.values())

    def ids(self) -> list[str]:
        """Return active connector ids."""

        return list(self._services)

    def inspect(self, connector_id: str) -> ConnectorInspectionSnapshot:
        """Return a connector inspection snapshot."""

        service = self.get(connector_id)
        if service is None or not hasattr(service, "inspect_snapshot"):
            return _empty_snapshot()
        snapshot = service.inspect_snapshot()
        return list(snapshot) if isinstance(snapshot, list) else _empty_snapshot()

    def request_source(self, connector_id: str, owner: str, source_name: str) -> bool:
        """Request a connector source."""

        service = self.get(connector_id)
        if service is None or not hasattr(service, "request_source"):
            return False
        requested = bool(service.request_source(owner, source_name))
        if requested:
            self._source_requests.setdefault(connector_id, {})[owner] = source_name
        return requested

    def release_source(self, connector_id: str, owner: str) -> bool:
        """Release a connector source claim."""

        service = self.get(connector_id)
        if service is None or not hasattr(service, "release_source"):
            return False
        released = bool(service.release_source(owner))
        if released:
            requests = self._source_requests.get(connector_id)
            if requests is not None:
                requests.pop(owner, None)
                if not requests:
                    self._source_requests.pop(connector_id, None)
        return released

    def source_requested(self, connector_id: str, source_name: str) -> bool:
        """Return whether a source has an active runtime request."""

        requests = self._source_requests.get(connector_id)
        if requests is None:
            return False
        return source_name in requests.values()

    def update(self, connector_id: str) -> bool:
        """Advance one connector service when supported."""

        service = self.get(connector_id)
        if service is None or not hasattr(service, "update"):
            return False
        service.update()
        return True
