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

"""Connector-owned manifest schemas."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ConnectorGameDecl:
    """Connector game support declaration from a plugin manifest."""

    id: str
    detect_names: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ConnectorServiceDecl:
    """Connector service declaration from a plugin manifest."""

    module: str
    class_name: str


@dataclass(frozen=True)
class ConnectorRuntimeDecl:
    """Connector runtime handoff declaration from a plugin manifest."""

    game_state_hook: str = ""


@dataclass(frozen=True)
class ConnectorManifest:
    """Connector-specific manifest declarations."""

    provides: list[str] = field(default_factory=list)
    games: list[ConnectorGameDecl] = field(default_factory=list)
    service: ConnectorServiceDecl | None = None
    runtime: ConnectorRuntimeDecl | None = None
