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

"""Small synchronous rFactor 2 shared-memory runtime for the connector family."""
# pyright: reportArgumentType=false

from __future__ import annotations

import math
from ctypes import Structure
from typing import cast

from . import _rFactor2_data as rF2data
from ._rFactor2_mmap import (
    INVALID_INDEX,
    MMapControl,
    rFactor2Constants,
)
from ._raw_dump import annotate_rows, iter_raw_fields


def bytes_to_str(value: object) -> str:
    if isinstance(value, bytes):
        return value.rstrip(b"\x00").decode("utf-8", errors="replace")
    return str(value)


def number_or_zero(value: object) -> float:
    if not isinstance(value, int | float):
        return 0.0
    result = float(value)
    return result if math.isfinite(result) else 0.0


def _fmt_mapping(value: object, mapped_to: str | None = None) -> str:
    rendered = str(value)
    if mapped_to is None:
        return rendered
    return f"{rendered} -> {mapped_to}"


def _raw_int(value: object) -> int:
    if isinstance(value, bytes):
        return int.from_bytes(value, byteorder="little", signed=False)
    return int(value)


_RAW_MAPPING_HINTS = {
    "raw.extended.mVersion": "state.version",
    "raw.scoring_info.mTrackName": "session.track_name / track.name",
    "raw.scoring_info.mSession": "session.session_kind",
    "raw.scoring_info.mCurrentET": "session.session_time_elapsed",
    "raw.scoring_info.mEndET": "session.session_time_left",
    "raw.scoring_info.mTrackTemp": "session.track_temperature",
    "raw.scoring_info.mAmbientTemp": "session.ambient_temperature",
    "raw.scoring_info.mRaining": "session.raininess",
    "raw.player_scoring.mDriverName": "vehicle.driver_name",
    "raw.player_scoring.mVehicleName": "vehicle.vehicle_name",
    "raw.player_scoring.mVehicleClass": "vehicle.class_name",
    "raw.player_scoring.mPlace": "vehicle.place",
    "raw.player_scoring.mInPits": "vehicle.in_pits",
    "raw.player_scoring.mLapDist": "lap.lap_distance",
    "raw.player_scoring.mLastLapTime": "timing.last_laptime",
    "raw.player_scoring.mBestLapTime": "timing.best_laptime",
    "raw.player_scoring.mTimeBehindLeader": "timing.gap_to_leader",
    "raw.player_telemetry.mFuel": "vehicle.fuel",
    "raw.player_telemetry.mGear": "engine.gear",
    "raw.player_telemetry.mEngineRPM": "engine.rpm",
    "raw.player_telemetry.mEngineMaxRPM": "engine.rpm_max",
    "raw.player_telemetry.mRearBrakeBias": "brake.bias_front",
    "raw.player_telemetry.mBatteryChargeFraction": "electric_motor.battery_charge",
    "raw.player_telemetry.mHeadlights": "switch.headlights",
    "raw.player_telemetry.mSpeedLimiter": "switch.speed_limiter",
    "raw.player_telemetry.mRearFlapLegalStatus": "switch.drs_status",
}


class RF2Info:
    """Minimal synchronous RF2 shared-memory view."""

    def __init__(self) -> None:
        self._scor = MMapControl(
            rFactor2Constants.MM_SCORING_FILE_NAME,
            cast(type[Structure], rF2data.rF2Scoring),
        )  # pyright: ignore[reportArgumentType]
        self._tele = MMapControl(
            rFactor2Constants.MM_TELEMETRY_FILE_NAME,
            cast(type[Structure], rF2data.rF2Telemetry),
        )  # pyright: ignore[reportArgumentType]
        self._ext = MMapControl(
            rFactor2Constants.MM_EXTENDED_FILE_NAME,
            cast(type[Structure], rF2data.rF2Extended),
        )  # pyright: ignore[reportArgumentType]
        self._ffb = MMapControl(
            rFactor2Constants.MM_FORCE_FEEDBACK_FILE_NAME,
            cast(type[Structure], rF2data.rF2ForceFeedback),
        )  # pyright: ignore[reportArgumentType]
        self._tele_indexes = {_index: _index for _index in range(128)}
        self._player_scor_index = INVALID_INDEX
        self._player_tele_index = INVALID_INDEX
        self._opened = False
        self._paused = True

    def open(self) -> None:
        self._scor.create(0, "")
        self._tele.create(0, "")
        self._ext.create(1, "")
        self._ffb.create(1, "")
        self._opened = True
        self.update()

    def close(self) -> None:
        if not self._opened:
            return
        self._ffb.close()
        self._ext.close()
        self._tele.close()
        self._scor.close()
        self._opened = False
        self._paused = True
        self._player_scor_index = INVALID_INDEX
        self._player_tele_index = INVALID_INDEX

    def update(self) -> None:
        if not self._opened:
            return
        if self._scor.update is not None:
            self._scor.update()
        if self._tele.update is not None:
            self._tele.update()
        self._sync_indexes()

    @property
    def rf2ScorInfo(self) -> rF2data.rF2ScoringInfo:
        return self._require_scor_data().mScoringInfo

    def rf2ScorVeh(self, index: int | None = None) -> rF2data.rF2VehicleScoring:
        data = self._require_scor_data()
        if index is None:
            index = self._player_scor_index
        if index < 0:
            return data.mVehicles[0]
        return data.mVehicles[index]

    def rf2TeleVeh(self, index: int | None = None) -> rF2data.rF2VehicleTelemetry:
        tele_data = self._require_tele_data()
        scor_data = self._require_scor_data()
        if index is None:
            index = self._player_tele_index
        elif index >= 0:
            index = self._tele_indexes.get(int(scor_data.mVehicles[index].mID), INVALID_INDEX)
        if index < 0:
            return tele_data.mVehicles[0]
        return tele_data.mVehicles[index]

    @property
    def rf2Ext(self) -> rF2data.rF2Extended:
        data = self._ext.data
        if data is None:
            raise RuntimeError("RF2 extended buffer is not open")
        return cast(rF2data.rF2Extended, data)

    @property
    def rf2Ffb(self) -> rF2data.rF2ForceFeedback:
        data = self._ffb.data
        if data is None:
            raise RuntimeError("RF2 force feedback buffer is not open")
        return cast(rF2data.rF2ForceFeedback, data)

    @property
    def playerIndex(self) -> int:
        return self._player_scor_index

    @property
    def isPaused(self) -> bool:
        return self._paused

    @property
    def isActive(self) -> bool:
        if self._paused or self._player_scor_index < 0:
            return False
        return bool(self.rf2ScorInfo.mInRealtime or self.rf2TeleVeh().mIgnitionStarter > 0)

    def raw_snapshot(self) -> list[tuple[str, str]]:
        scor = self.rf2ScorInfo
        player_scor = self.rf2ScorVeh()
        player_tele = self.rf2TeleVeh()
        wheels = player_tele.mWheels
        snapshot = [
            ("mapped.extended.mVersion", _fmt_mapping(bytes_to_str(self.rf2Ext.mVersion), "state.version")),
            ("mapped.scoring.mTrackName", _fmt_mapping(bytes_to_str(scor.mTrackName), "session.track_name / track.name")),
            ("mapped.scoring.mSession", _fmt_mapping(int(scor.mSession), "session.session_kind")),
            ("mapped.scoring.mCurrentET", _fmt_mapping(f"{number_or_zero(scor.mCurrentET):.3f}", "session.session_time_elapsed")),
            ("mapped.scoring.mEndET", _fmt_mapping(f"{number_or_zero(scor.mEndET):.3f}", "session.session_time_left")),
            ("mapped.scoring.mTrackTemp", _fmt_mapping(f"{number_or_zero(scor.mTrackTemp):.2f}", "session.track_temperature")),
            ("mapped.scoring.mAmbientTemp", _fmt_mapping(f"{number_or_zero(scor.mAmbientTemp):.2f}", "session.ambient_temperature")),
            ("mapped.scoring.mRaining", _fmt_mapping(f"{number_or_zero(scor.mRaining):.3f}", "session.raininess")),
            ("mapped.telemetry.playerIndex", _fmt_mapping(self.playerIndex, "vehicle.player_index")),
            ("mapped.telemetry.mVehicleName", _fmt_mapping(bytes_to_str(player_scor.mVehicleName), "vehicle.vehicle_name")),
            ("mapped.telemetry.mFuel", _fmt_mapping(f"{number_or_zero(player_tele.mFuel):.2f}", "vehicle.fuel")),
            ("mapped.telemetry.mGear", _fmt_mapping(int(player_tele.mGear), "engine.gear")),
            ("mapped.telemetry.mEngineRPM", _fmt_mapping(f"{number_or_zero(player_tele.mEngineRPM):.1f}", "engine.rpm")),
            ("mapped.telemetry.mRearBrakeBias", _fmt_mapping(f"{number_or_zero(player_tele.mRearBrakeBias):.3f}", "brake.bias_front")),
            ("mapped.telemetry.mBatteryChargeFraction", _fmt_mapping(f"{number_or_zero(player_tele.mBatteryChargeFraction):.3f}", "electric_motor.battery_charge")),
            ("mapped.telemetry.mRearFlapLegalStatus", _fmt_mapping(int(player_tele.mRearFlapLegalStatus), "switch.drs_status")),
            ("mapped.scoring.mPlace", _fmt_mapping(int(player_scor.mPlace), "vehicle.place")),
            ("mapped.scoring.mInPits", _fmt_mapping(bool(player_scor.mInPits), "vehicle.in_pits")),
            ("candidate.telemetry.mScheduledStops", str(int(player_tele.mScheduledStops))),
            ("candidate.scoring.mNumPitstops", str(int(player_scor.mNumPitstops))),
            ("candidate.scoring.mFlag", str(int(player_scor.mFlag))),
            ("candidate.scoring.mYellowFlagState", str(_raw_int(scor.mYellowFlagState))),
            ("candidate.scoring.mWind", f"{number_or_zero(scor.mWind.x):.2f}, {number_or_zero(scor.mWind.y):.2f}, {number_or_zero(scor.mWind.z):.2f}"),
            ("candidate.telemetry.mRearFlapActivated", str(int(player_tele.mRearFlapActivated))),
            ("candidate.telemetry.mWheels[0].mSurfaceType", str(int(wheels[0].mSurfaceType))),
            ("candidate.telemetry.mWheels[0].mGripFract", f"{number_or_zero(wheels[0].mGripFract):.3f}"),
        ]
        snapshot.extend(
            annotate_rows(
                [
                    *iter_raw_fields(self.rf2Ext, "raw.extended"),
                    *iter_raw_fields(scor, "raw.scoring_info"),
                    *iter_raw_fields(player_scor, "raw.player_scoring"),
                    *iter_raw_fields(player_tele, "raw.player_telemetry"),
                ],
                _RAW_MAPPING_HINTS,
            )
        )
        return snapshot

    def _sync_indexes(self) -> None:
        tele_data = self._require_tele_data()
        for tele_idx in range(int(tele_data.mNumVehicles)):
            veh_info = tele_data.mVehicles[tele_idx]
            self._tele_indexes[int(veh_info.mID)] = tele_idx

        self._player_scor_index = INVALID_INDEX
        scor_data = self._require_scor_data()
        for scor_idx in range(int(scor_data.mScoringInfo.mNumVehicles)):
            if scor_data.mVehicles[scor_idx].mIsPlayer:
                self._player_scor_index = scor_idx
                break

        if self._player_scor_index < 0:
            self._player_tele_index = INVALID_INDEX
            self._paused = True
            return

        player_id = int(scor_data.mVehicles[self._player_scor_index].mID)
        self._player_tele_index = self._tele_indexes.get(player_id, INVALID_INDEX)
        self._paused = self._player_tele_index < 0

    def _require_scor_data(self) -> rF2data.rF2Scoring:
        data = self._scor.data
        if data is None:
            raise RuntimeError("RF2 scoring buffer is not open")
        return cast(rF2data.rF2Scoring, data)

    def _require_tele_data(self) -> rF2data.rF2Telemetry:
        data = self._tele.data
        if data is None:
            raise RuntimeError("RF2 telemetry buffer is not open")
        return cast(rF2data.rF2Telemetry, data)
