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

"""Read capability for connector game detection state."""

from __future__ import annotations

from runtimeV2.connectors.game_detector_store import ConnectorGameDetectorStore


class ConnectorGameDetectorRead:
    """Read detected host games for connector families."""

    def __init__(self, store: ConnectorGameDetectorStore) -> None:
        self._store = store

    def detected_game(self, connector_id: str) -> str | None:
        """Return the detected game id for one connector family when available."""

        record = self._store.get(connector_id)
        return None if record is None else record.game_id

    def process_name(self, connector_id: str) -> str | None:
        """Return the matched process name for one connector family when available."""

        record = self._store.get(connector_id)
        return None if record is None else record.process_name

    def has_game(self, connector_id: str) -> bool:
        """Return True when a supported game process is currently detected."""

        return self._store.get(connector_id) is not None
