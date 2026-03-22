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
"""TyreDemoViewModel — exposes live tyre data from the LMU connector to QML.

Attempts to connect directly to LMU shared memory.
Shows '-' or 0 values when the game is not active.
"""

from __future__ import annotations

import sys
from pathlib import Path

import psutil

from PySide6.QtCore import Property, QObject, QTimer, Signal

from tinyui.log import get_logger

log = get_logger(__name__)

# Add LMU submodule to path
_LMU_LIB = Path(__file__).resolve().parents[2] / "plugins" / "demo"
if str(_LMU_LIB) not in sys.path:
    sys.path.insert(0, str(_LMU_LIB))


# TODO: connector should be provided via the plugin context (ctx.connector), not instantiated directly
def _load_connector():
    """Load the LMU connector — returns None if the library is not available."""
    log.connector("LMU lib path", path=str(_LMU_LIB), exists=_LMU_LIB.exists())
    log.connector("sys.path check", in_path=str(_LMU_LIB) in sys.path)
    try:
        from plugins.demo.connector.lmu import LMUConnector  # type: ignore[import]
        log.connector("LMUConnector imported")
        c = LMUConnector()
        c.open()
        log.connector("shared memory opened")
        return c
    except Exception as exc:
        log.warning("LMU connector not available: %s (%s)", exc, type(exc).__name__)
        return None


_TYRE_LABELS = ("FL", "FR", "RL", "RR")


class TyreDemoViewModel(QObject):
    """Polls the LMU connector every 100 ms and exposes tyre data to QML."""

    tyreDataChanged = Signal()

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)

        self._connector    = _load_connector()
        self._game_running = False
        self._active       = False
        self._version      = "–"
        self._compound     = ("–", "–")  # (front, rear)

        # Previous state for change detection
        self._prev_game_running = None
        self._prev_active       = None
        self._prev_game_phase   = None

        # Process check every 2s — psutil is too heavy for every 100ms poll
        self._process_check_counter = 0

        # 4 tyres × 4 values: surface_temp, inner_temp, pressure, wear
        self._surface  = [0.0] * 4
        self._inner    = [0.0] * 4
        self._pressure = [0.0] * 4
        self._wear     = [0.0] * 4

        self._timer = QTimer(self)
        self._timer.setInterval(100)
        self._timer.timeout.connect(self._poll)
        if self._connector is not None:
            self._timer.start()
            log.info("TyreDemoViewModel: LMU connector active — polling started")

    # ── Poll ──────────────────────────────────────────────────────────────────

    def _poll(self) -> None:
        c = self._connector
        if c is None:
            return
        try:
            c.update()

            # Process check every 2s (20 × 100ms) — psutil is too heavy for every poll
            self._process_check_counter += 1
            if self._process_check_counter >= 20:
                self._process_check_counter = 0
                self._game_running = any(
                    p.info["name"].lower() in ("lmu.exe", "rfactor2.exe")
                    for p in psutil.process_iter(["name"])
                )

            self._active   = self._game_running and c.state.active()
            game_phase     = int(c._info.data.scoring.scoringInfo.mGamePhase)

            # Only log on state change
            if (self._game_running != self._prev_game_running
                    or self._active != self._prev_active
                    or game_phase   != self._prev_game_phase):
                log.connector("state changed",
                    game_running=self._game_running,
                    active=self._active,
                    playerHasVehicle=bool(c._info.data.telemetry.playerHasVehicle),
                    gamePhase=game_phase,
                )
                self._prev_game_running = self._game_running
                self._prev_active       = self._active
                self._prev_game_phase   = game_phase
            self._version = c.state.version() if self._game_running else "–"

            if self._game_running:
                self._compound = c.tyre.compound_name()
            else:
                self._compound = ("–", "–")

            if self._active:
                self._surface  = list(c.tyre.surface_temperature())
                self._inner    = list(c.tyre.inner_temperature())
                self._pressure = list(c.tyre.pressure())
                self._wear     = list(c.tyre.wear())
            else:
                self._surface  = [0.0] * 4
                self._inner    = [0.0] * 4
                self._pressure = [0.0] * 4
                self._wear     = [0.0] * 4

        except Exception as exc:
            log.warning("poll fout: %s", exc)
            self._game_running = False

        self.tyreDataChanged.emit()

    # ── Properties ────────────────────────────────────────────────────────────

    @Property(bool, notify=tyreDataChanged)
    def connected(self) -> bool:
        """Shared memory reachable (connector loaded)."""
        return self._connector is not None

    @Property(bool, notify=tyreDataChanged)
    def gameRunning(self) -> bool:
        """LMU is active and writing to shared memory."""
        return self._game_running

    @Property(bool, notify=tyreDataChanged)
    def active(self) -> bool:
        """Player is on track and data is live."""
        return self._active

    @Property(str, notify=tyreDataChanged)
    def gameVersion(self) -> str:
        return self._version

    @Property(str, notify=tyreDataChanged)
    def compoundFront(self) -> str:
        return self._compound[0]

    @Property(str, notify=tyreDataChanged)
    def compoundRear(self) -> str:
        return self._compound[1]

    @Property("QVariantList", notify=tyreDataChanged)
    def tyres(self) -> list[dict]:
        """List of 4 tyres, each a dict with label and values."""
        return [
            {
                "label":    _TYRE_LABELS[i],
                "surface":  round(self._surface[i],  1),
                "inner":    round(self._inner[i],    1),
                "pressure": round(self._pressure[i], 2),
                "wear":     round(self._wear[i],     3),
            }
            for i in range(4)
        ]

    def shutdown(self) -> None:
        self._timer.stop()
        if self._connector is not None:
            try:
                self._connector.close()
            except Exception:
                pass
