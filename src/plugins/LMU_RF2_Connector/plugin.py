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

"""Connector family entrypoints and hooks for the consolidated LMU/rF2 family."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .service import create_lmu_rf2_service

if TYPE_CHECKING:
    from runtimeV2.connectors.contracts import ConnectorGameStateUpdate


_LIVE_GAMES = frozenset({"lmu", "rf2"})
_LIVE_SOURCES = frozenset({"lmu", "rf2"})
_last_game_state: dict[str, str | bool] = {
    "active_source": "none",
    "active_game": "none",
    "is_live": False,
}


class LMURF2Connector:
    """Host-side connector service entrypoint for the LMU/rF2 family."""

    def __new__(cls):
        return create_lmu_rf2_service()


def update_game_state(update: "ConnectorGameStateUpdate") -> dict[str, bool]:
    """Receive manifest-declared game-state updates from runtime V2 connectors."""

    _last_game_state["active_source"] = update.active_source
    _last_game_state["active_game"] = update.active_game
    _last_game_state["is_live"] = update.is_live
    return {
        "show_widgets": _should_show_widgets(update),
    }


def _should_show_widgets(update: "ConnectorGameStateUpdate") -> bool:
    """Return True when the family is attached to a real supported game source."""

    if not update.is_live:
        return False
    if update.active_source not in _LIVE_SOURCES:
        return False
    if update.active_game not in _LIVE_GAMES:
        return False
    return True
