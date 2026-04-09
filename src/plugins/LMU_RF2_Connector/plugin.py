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

from .shared_memory._rFactor2_data import rF2GamePhase
from .service import LMURF2ConnectorService, create_lmu_rf2_service

if TYPE_CHECKING:
    from runtimeV2.connectors.contracts import ConnectorGameStateUpdate


_SUPPORTED_LIVE_GAMES = frozenset({"lmu", "rf2"})
_SUPPORTED_LIVE_SOURCES = frozenset({"lmu", "rf2"})
_VISIBLE_GAME_PHASES = frozenset(
    {
        int(rF2GamePhase.WarmUp.value),
        int(rF2GamePhase.GridWalk.value),
        int(rF2GamePhase.Formation.value),
        int(rF2GamePhase.Countdown.value),
        int(rF2GamePhase.GreenFlag.value),
        int(rF2GamePhase.FullCourseYellow.value),
    }
)
_service_instance: LMURF2ConnectorService | None = None


class LMURF2Connector:
    """Host-side connector service entrypoint for the LMU/rF2 family."""

    def __new__(cls):
        return create_service()


def create_service():
    """Create the family service instance declared by the connector manifest."""

    global _service_instance
    if _service_instance is None:
        _service_instance = create_lmu_rf2_service()
    return _service_instance


def update_game_state(update: "ConnectorGameStateUpdate") -> dict[str, bool]:
    """Receive manifest-declared game-state updates from runtime V2 connectors."""

    return {
        "show_widgets": _should_show_widgets(update),
    }


def _should_show_widgets(update: "ConnectorGameStateUpdate") -> bool:
    """Return True when the family reports the player being in-car during visible phases."""

    service = _service_instance
    if service is None:
        return False
    if not update.is_live:
        return False
    if update.active_source not in _SUPPORTED_LIVE_SOURCES:
        return False
    if update.active_game not in _SUPPORTED_LIVE_GAMES:
        return False
    if service.in_realtime() is not True:
        return False
    if service.state.active() is not True:
        return False
    if service.state.paused() is True:
        return False
    if service.has_player_vehicle() is not True:
        return False
    if service.game_phase() not in _VISIBLE_GAME_PHASES:
        return False
    return True
