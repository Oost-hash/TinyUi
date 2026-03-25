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
"""Shared LMU data source."""

from __future__ import annotations

from tinycore.log import get_logger

from .shared import _SESSION_NAMES, MMapControl, LMUConstants, lmu_data

_log = get_logger(__name__)


class LMUSource:
    """Single owner of the LMU shared memory connection."""

    def __init__(self) -> None:
        self._info = MMapControl(
            LMUConstants.LMU_SHARED_MEMORY_FILE,
            lmu_data.LMUObjectOut,
        )
        self._prev_active: bool | None = None
        self._prev_paused: bool | None = None
        self._prev_session_type: int | None = None
        self._prev_track: str | None = None

    @property
    def info(self) -> MMapControl:
        return self._info

    def open(self) -> None:
        self._info.create()
        _log.info("LMU shared memory opened  version=%s", self.info.data.generic.gameVersion)

    def close(self) -> None:
        self._info.close()
        _log.info("LMU shared memory closed")

    def update(self) -> None:
        self._info.update()
        self._log_transitions()

    def _session_type(self) -> int:
        raw = int(self.info.data.scoring.scoringInfo.mSession)
        if raw == 0:
            return 0
        if 1 <= raw <= 4:
            return 1
        if 5 <= raw <= 8:
            return 2
        if raw == 9:
            return 3
        return 4

    def _log_transitions(self) -> None:
        try:
            phase = int(self.info.data.scoring.scoringInfo.mGamePhase)
            active = bool(
                self.info.data.telemetry.playerHasVehicle
                and phase not in (0, 7, 8, 9)
            )
            paused = phase == 9
        except Exception:
            return

        if active != self._prev_active:
            if active:
                self._log_session_start()
            elif self._prev_active is not None:
                _log.info("game stopped")
            self._prev_active = active

        if active:
            try:
                session = self.info.data.scoring.scoringInfo
                stype = self._session_type()
                track = session.mTrackName.rstrip(b"\x00").decode("utf-8", errors="replace")
                if self._prev_session_type is not None and stype != self._prev_session_type:
                    _log.info("session changed  session=%s", _SESSION_NAMES.get(stype, stype))
                if self._prev_track is not None and track != self._prev_track:
                    _log.info("track changed  track=%s", track)
                self._prev_session_type = stype
                self._prev_track = track
            except Exception:
                pass
        else:
            self._prev_session_type = None
            self._prev_track = None

        if paused != self._prev_paused and self._prev_paused is not None:
            _log.info("game %s", "paused" if paused else "resumed")
        self._prev_paused = paused

    def _log_session_start(self) -> None:
        try:
            session = self.info.data.scoring.scoringInfo
            player_idx = self.info.data.telemetry.playerVehicleIdx
            veh = self.info.data.scoring.vehScoringInfo[player_idx]
            telem = self.info.data.telemetry.telemInfo[player_idx]
            stype = self._session_type()
            track = session.mTrackName.rstrip(b"\x00").decode("utf-8", errors="replace")
            driver = veh.mDriverName.rstrip(b"\x00").decode("utf-8", errors="replace")
            car = telem.mVehicleName.rstrip(b"\x00").decode("utf-8", errors="replace")
            cls = veh.mVehicleClass.rstrip(b"\x00").decode("utf-8", errors="replace")
            cars = int(session.mNumVehicles)
            t_track = float(session.mTrackTemp)
            t_amb = float(session.mAmbientTemp)
            version = str(self.info.data.generic.gameVersion)
            _log.info(
                "game started  session=%s  track=%s  driver=%s  car=%s  class=%s"
                "  cars=%d  t_track=%.1f°C  t_amb=%.1f°C  version=%s",
                _SESSION_NAMES.get(stype, stype),
                track,
                driver,
                car,
                cls,
                cars,
                t_track,
                t_amb,
                version,
            )
            self._prev_session_type = stype
            self._prev_track = track
        except Exception as exc:
            _log.info("game started  (context unavailable: %s)", exc)
