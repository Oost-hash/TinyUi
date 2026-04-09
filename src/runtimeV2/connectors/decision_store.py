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

"""Connector-owned game-state decision store."""

from __future__ import annotations

from runtimeV2.connectors.contracts import ConnectorGameStateDecision


class ConnectorGameStateDecisionStore:
    """Store connector policy decisions derived from plugin game-state hooks."""

    def __init__(self) -> None:
        self._decisions: dict[str, ConnectorGameStateDecision] = {}

    def set(self, connector_id: str, decision: ConnectorGameStateDecision) -> None:
        """Store the latest decision for one connector."""

        self._decisions[connector_id] = decision

    def get(self, connector_id: str) -> ConnectorGameStateDecision | None:
        """Return the latest decision for one connector when available."""

        return self._decisions.get(connector_id)
