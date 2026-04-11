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

"""Public connector contracts used outside the connectors domain."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from runtimeV2.connectors.contracts import ConnectorInspectionSnapshot, ConnectorServiceRecord
from runtimeV2.connectors.game_detector_store import DetectedConnectorGame


@runtime_checkable
class ConnectorReader(Protocol):
    """Public contract for reading connector service registry state."""

    def services(self) -> list[ConnectorServiceRecord]:
        """Return active connector service records."""
        ...

    def ids(self) -> list[str]:
        """Return active connector ids."""
        ...

    def has(self, connector_id: str) -> bool:
        """Return True when a connector is active."""
        ...

    def service(self, connector_id: str) -> ConnectorServiceRecord | None:
        """Return one connector service record."""
        ...

    def inspection_rows(self, connector_id: str) -> ConnectorInspectionSnapshot:
        """Return connector inspection rows."""
        ...

    def inspection_map(self, connector_id: str) -> dict[str, str]:
        """Return one connector inspection snapshot keyed by name."""
        ...

    def value(self, connector_id: str, key: str) -> str | None:
        """Return one inspection value by key."""
        ...

    def active_source(self, connector_id: str) -> str | None:
        """Return the active source name for one connector service when available."""
        ...

    def source_requested(self, connector_id: str, source_name: str) -> bool:
        """Return whether a source has an active runtime request."""
        ...

    def active_game(self, connector_id: str) -> str | None:
        """Return the active game name for one connector service when available."""
        ...

    def state_active(self, connector_id: str) -> bool | None:
        """Return whether one connector reports an active in-session state."""
        ...

    def state_paused(self, connector_id: str) -> bool | None:
        """Return whether one connector reports a paused session state."""
        ...

    def show_widgets(self, connector_id: str) -> bool | None:
        """Return the connector-owned widget visibility decision when available."""
        ...

    def detected_game(self, connector_id: str) -> str | None:
        """Return the runtime-detected host game id when available."""
        ...

    def detected_process_name(self, connector_id: str) -> str | None:
        """Return the runtime-detected host process name when available."""
        ...


@runtime_checkable
class ConnectorWriter(Protocol):
    """Public contract for controlling connector service sources and updates."""

    def request_source(self, connector_id: str, owner: str, source_name: str) -> bool:
        """Request a connector source."""
        ...

    def release_source(self, connector_id: str, owner: str) -> bool:
        """Release a connector source claim."""
        ...

    def update(self, connector_id: str) -> bool:
        """Update one connector service."""
        ...

    def update_all(self) -> list[str]:
        """Update all connector services."""
        ...


@runtime_checkable
class ConnectorGameDetectorReader(Protocol):
    """Public contract for reading detected host games for connector families."""

    def detected_game(self, connector_id: str) -> str | None:
        """Return the detected game id for one connector family when available."""
        ...

    def process_name(self, connector_id: str) -> str | None:
        """Return the matched process name for one connector family when available."""
        ...

    def has_game(self, connector_id: str) -> bool:
        """Return True when a supported game process is currently detected."""
        ...


@runtime_checkable
class ConnectorGameDetectorWriter(Protocol):
    """Public contract for driving host game detection for connector families."""

    def sync(self, connector_id: str) -> DetectedConnectorGame | None:
        """Detect and persist the current host game for one connector family."""
        ...
