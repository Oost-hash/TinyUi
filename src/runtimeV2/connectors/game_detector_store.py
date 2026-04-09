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

"""Store for connector game detection state."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DetectedConnectorGame:
    """Detected host game for one connector family."""

    connector_id: str
    plugin_id: str
    game_id: str
    process_name: str


class ConnectorGameDetectorStore:
    """Keep the latest detected game per connector family."""

    def __init__(self) -> None:
        self._records: dict[str, DetectedConnectorGame] = {}

    def get(self, connector_id: str) -> DetectedConnectorGame | None:
        """Return the current detected game record for one connector."""

        return self._records.get(connector_id)

    def set(self, connector_id: str, record: DetectedConnectorGame | None) -> None:
        """Replace the detected game record for one connector."""

        if record is None:
            self._records.pop(connector_id, None)
            return
        self._records[connector_id] = record
