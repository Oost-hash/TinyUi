"""Connector service runtime contracts."""

from __future__ import annotations

from typing import Any, Protocol


ConnectorInspectionSnapshot = list[tuple[str, str]]


class ConnectorServiceAccess(Protocol):
    """Read-only and control access to active connector services."""

    def has(self, connector_id: str) -> bool:
        """Return True when the connector service is active."""
        ...

    def get(self, connector_id: str) -> Any | None:
        """Return the raw connector service instance when available."""
        ...

    def inspect(self, connector_id: str) -> ConnectorInspectionSnapshot:
        """Return a snapshot for diagnostics and UI rendering."""
        ...

    def request_source(self, connector_id: str, owner: str, source_name: str) -> bool:
        """Request a specific source for a connector service."""
        ...

    def release_source(self, connector_id: str, owner: str) -> bool:
        """Release a previous source request for a connector service."""
        ...

    def update(self, connector_id: str) -> bool:
        """Advance the connector service once when supported."""
        ...
