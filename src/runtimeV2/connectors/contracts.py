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

"""Contracts for runtime V2 connector services."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


ConnectorInspectionSnapshot = list[tuple[str, str]]


@dataclass(frozen=True)
class ConnectorServiceRecord:
    """Connector service instance and metadata."""

    connector_id: str
    plugin_id: str
    display_name: str
    instance: Any


@dataclass(frozen=True)
class ConnectorServiceRegisteredData:
    """Event payload for connector service registration."""

    connector_id: str
    plugin_id: str
    display_name: str


@dataclass(frozen=True)
class ConnectorServiceUnregisteredData:
    """Event payload for connector service removal."""

    connector_id: str
    plugin_id: str


@dataclass(frozen=True)
class ConnectorServiceUpdatedData:
    """Event payload for connector service updates."""

    connector_id: str
    plugin_id: str


@dataclass(frozen=True)
class ConnectorSourceChangedData:
    """Event payload for connector source ownership changes."""

    connector_id: str
    plugin_id: str
    owner: str
    source_name: str
    action: str


@dataclass(frozen=True)
class ConnectorGameStateUpdate:
    """Small connector game-state handoff for plugin.py hooks."""

    connector_id: str
    plugin_id: str
    active_source: str
    active_game: str
    is_live: bool


@dataclass(frozen=True)
class ConnectorGameStateDecision:
    """Connector-owned policy switches derived from game-state updates."""

    show_widgets: bool | None = None
