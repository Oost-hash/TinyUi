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
"""TyreDemoViewModel — exposeert live bandendata van de LMU connector aan QML.

Probeert direct verbinding te maken met LMU shared memory.
Toont '-' of 0 waardes wanneer het spel niet actief is.
"""

from __future__ import annotations

import sys
from pathlib import Path

import psutil

from PySide6.QtCore import Property, QObject, QTimer, Signal

from tinyui.log import get_logger

log = get_logger(__name__)

# LMU submodule op het pad zetten
_LMU_LIB = Path(__file__).resolve().parents[2] / "plugins" / "demo"
if str(_LMU_LIB) not in sys.path:
    sys.path.insert(0, str(_LMU_LIB))


def _load_connector():
    """Laad de LMU connector — None als de library niet beschikbaar is."""
    log.connector("LMU lib pad", path=str(_LMU_LIB), exists=_LMU_LIB.exists())
    log.connector("sys.path check", in_path=str(_LMU_LIB) in sys.path)
    try:
        from plugins.demo.connector.lmu import LMUConnector  # type: ignore[import]
        log.connector("LMUConnector geïmporteerd")
        c = LMUConnector()
        c.open()
        log.connector("shared memory geopend")
        return c
    except Exception as exc:
        log.warning("LMU connector niet beschikbaar: %s (%s)", exc, type(exc).__name__)
        return None


_TYRE_LABELS = ("FL", "FR", "RL", "RR")


class TyreDemoViewModel(QObject):
    """Pollt de LMU connector elke 100 ms en exposeert bandendata aan QML."""

    tyreDataChanged = Signal()

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)

        self._connector    = _load_connector()
        self._game_running = False
        self._active       = False
        self._version      = "–"
        self._compound     = ("–", "–")  # (front, rear)

        # Vorige state voor change-detection
        self._prev_game_running = None
        self._prev_active       = None
        self._prev_game_phase   = None

        # Process check elke 2s — psutil is te zwaar voor elke 100ms poll
        self._process_check_counter = 0

        # 4 banden × 4 waarden: surface_temp, inner_temp, pressure, wear
        self._surface  = [0.0] * 4
        self._inner    = [0.0] * 4
        self._pressure = [0.0] * 4
        self._wear     = [0.0] * 4

        self._timer = QTimer(self)
        self._timer.setInterval(100)
        self._timer.timeout.connect(self._poll)
        if self._connector is not None:
            self._timer.start()
            log.info("TyreDemoViewModel: LMU connector actief — polling gestart")

    # ── Poll ──────────────────────────────────────────────────────────────────

    def _poll(self) -> None:
        c = self._connector
        if c is None:
            return
        try:
            c.update()

            # Process check elke 2s (20 × 100ms) — psutil is te zwaar voor elke poll
            self._process_check_counter += 1
            if self._process_check_counter >= 20:
                self._process_check_counter = 0
                self._game_running = any(
                    p.info["name"].lower() in ("lmu.exe", "rfactor2.exe")
                    for p in psutil.process_iter(["name"])
                )

            self._active   = self._game_running and c.state.active()
            game_phase     = int(c._info.data.scoring.scoringInfo.mGamePhase)

            # Alleen loggen bij state wijziging
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
        """Shared memory bereikbaar (connector geladen)."""
        return self._connector is not None

    @Property(bool, notify=tyreDataChanged)
    def gameRunning(self) -> bool:
        """LMU is actief en schrijft naar shared memory."""
        return self._game_running

    @Property(bool, notify=tyreDataChanged)
    def active(self) -> bool:
        """Speler is op de baan en data is live."""
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
        """Lijst van 4 banden — elk een dict met label en waarden."""
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
