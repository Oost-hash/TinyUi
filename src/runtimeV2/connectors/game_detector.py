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

"""Runtime-owned process game detection for connector families."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
import re

import psutil

from runtimeV2.contracts import ConnectorGameDetectedData, ConnectorGameLostData
from runtimeV2.connectors.game_detector_store import ConnectorGameDetectorStore, DetectedConnectorGame
from runtimeV2.connectors.schemas.manifest import ConnectorManifest
from runtimeV2.contracts import EventBus, EventType


@dataclass(frozen=True)
class _ProcessInfo:
    name: str


class ConnectorGameDetector:
    """Detect supported games for connector families from manifest declarations."""

    def __init__(
        self,
        declarations: dict[str, ConnectorManifest],
        store: ConnectorGameDetectorStore,
        events: EventBus | None = None,
        *,
        process_provider=None,
    ) -> None:
        self._declarations = declarations
        self._store = store
        self._events = events
        self._process_provider = process_provider or self._iter_process_names

    def detect(self, connector_id: str) -> DetectedConnectorGame | None:
        """Detect and persist the current host game for one connector family."""

        declaration = self._declarations.get(connector_id)
        previous = self._store.get(connector_id)
        detected = self._detect_for_declaration(connector_id, declaration)
        if previous == detected:
            return detected
        self._store.set(connector_id, detected)
        self._emit_change(connector_id, previous, detected)
        return detected

    def _detect_for_declaration(
        self,
        connector_id: str,
        declaration: ConnectorManifest | None,
    ) -> DetectedConnectorGame | None:
        if declaration is None or not declaration.games:
            return None
        process_names = {self._normalize_name(name): name for name in self._process_provider()}
        for game in declaration.games:
            for detect_name in game.detect_names:
                process_name = process_names.get(self._normalize_name(detect_name))
                if process_name is None:
                    continue
                return DetectedConnectorGame(
                    connector_id=connector_id,
                    plugin_id=connector_id,
                    game_id=game.id,
                    process_name=process_name,
                )
        return None

    def _emit_change(
        self,
        connector_id: str,
        previous: DetectedConnectorGame | None,
        current: DetectedConnectorGame | None,
    ) -> None:
        if self._events is None:
            return
        if previous is not None and current is None:
            self._events.emit_typed(
                EventType.CONNECTOR_GAME_LOST,
                ConnectorGameLostData(
                    connector_id=connector_id,
                    plugin_id=previous.plugin_id,
                    game_id=previous.game_id,
                    process_name=previous.process_name,
                ),
                source="connectors",
            )
            return
        if current is not None:
            self._events.emit_typed(
                EventType.CONNECTOR_GAME_DETECTED,
                ConnectorGameDetectedData(
                    connector_id=connector_id,
                    plugin_id=current.plugin_id,
                    game_id=current.game_id,
                    process_name=current.process_name,
                ),
                source="connectors",
            )

    @staticmethod
    def _iter_process_names() -> Iterable[str]:
        for process in psutil.process_iter(attrs=["name"]):
            name = process.info.get("name")
            if isinstance(name, str) and name:
                yield name

    @staticmethod
    def _normalize_name(value: str) -> str:
        base = value.strip()
        if base.lower().endswith(".exe"):
            base = base[:-4]
        return re.sub(r"[^a-z0-9]+", "", base.casefold())


def validate_connector_detection_declarations(declarations: dict[str, ConnectorManifest]) -> None:
    """Require connector families to declare process detection names for runtime detection."""

    for connector_id, declaration in declarations.items():
        if declaration.service is None:
            continue
        if any(game.detect_names for game in declaration.games):
            continue
        raise ValueError(
            f"Connector '{connector_id}' must declare at least one connector.game.detect_names entry",
        )
