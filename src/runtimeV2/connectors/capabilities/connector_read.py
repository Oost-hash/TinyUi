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

from runtimeV2.connectors.decision_store import ConnectorGameStateDecisionStore
from runtimeV2.connectors.game_detector_store import ConnectorGameDetectorStore
from runtimeV2.connectors.contracts import ConnectorInspectionSnapshot, ConnectorServiceRecord
from runtimeV2.connectors.service_registry import ConnectorServiceRegistry


class ConnectorRead:
    """Read connector service registry state."""

    def __init__(
        self,
        registry: ConnectorServiceRegistry,
        decision_store: ConnectorGameStateDecisionStore | None = None,
        detector_store: ConnectorGameDetectorStore | None = None,
    ) -> None:
        self._registry = registry
        self._decision_store = decision_store
        self._detector_store = detector_store

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

    def state_active(self, connector_id: str) -> bool | None:
        """Return whether one connector reports an active in-session state."""

        service = self._registry.get(connector_id)
        if service is None or not hasattr(service, "state"):
            return None
        try:
            return bool(service.state.active())
        except Exception:
            return None

    def state_paused(self, connector_id: str) -> bool | None:
        """Return whether one connector reports a paused session state."""

        service = self._registry.get(connector_id)
        if service is None or not hasattr(service, "state"):
            return None
        try:
            return bool(service.state.paused())
        except Exception:
            return None

    def show_widgets(self, connector_id: str) -> bool | None:
        """Return the connector-owned widget visibility decision when available."""

        if self._decision_store is None:
            return None
        decision = self._decision_store.get(connector_id)
        if decision is None:
            return None
        return decision.show_widgets

    def detected_game(self, connector_id: str) -> str | None:
        """Return the runtime-detected host game id when available."""

        if self._detector_store is None:
            return None
        record = self._detector_store.get(connector_id)
        return None if record is None else record.game_id

    def detected_process_name(self, connector_id: str) -> str | None:
        """Return the runtime-detected host process name when available."""

        if self._detector_store is None:
            return None
        record = self._detector_store.get(connector_id)
        return None if record is None else record.process_name
