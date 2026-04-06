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
