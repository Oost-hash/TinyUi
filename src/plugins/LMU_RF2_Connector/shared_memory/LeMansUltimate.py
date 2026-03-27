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

"""Le Mans Ultimate shared-memory reader and telemetry bridge."""
# pyright: reportOptionalMemberAccess=false, reportOptionalCall=false, reportArgumentType=false

from __future__ import annotations

import math
from typing import cast

from tinycore.log import get_logger

from ..contracts.telemetry import Brake, ElectricMotor, Engine, Inputs, Lap, Session, State, Switch, Timing, Tyre, Vehicle, Wheel
from . import _LeMansUltimate_data as lmu_data
from ._LeMansUltimate_data import LMUConstants
from ._LeMansUltimate_mmap import MMapControl
_log = get_logger(__name__)
_KELVIN = 273.15
_SESSION_NAMES = {0: "test", 1: "practice", 2: "qualify", 3: "warmup", 4: "race"}
def decode_bytes(raw: bytes) -> str:
    return raw.rstrip(b"\x00").decode("utf-8", errors="replace")


class LMUSource:
    """Single owner of the LMU shared memory connection."""

    def __init__(self) -> None:
        self._info = MMapControl(LMUConstants.LMU_SHARED_MEMORY_FILE, lmu_data.LMUObjectOut)
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
            active = bool(self.info.data.telemetry.playerHasVehicle and phase not in (0, 7, 8, 9))
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
                track = decode_bytes(session.mTrackName)
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
            _log.info(
                "game started  session=%s  track=%s  driver=%s  car=%s  class=%s  cars=%d",
                _SESSION_NAMES.get(stype, stype),
                decode_bytes(session.mTrackName),
                decode_bytes(veh.mDriverName),
                decode_bytes(telem.mVehicleName),
                decode_bytes(veh.mVehicleClass),
                int(session.mNumVehicles),
            )
        except Exception as exc:
            _log.info("game started  (context unavailable: %s)", exc)


class LMUStateProvider(State):
    def __init__(self, source: LMUSource) -> None: self._source = source
    def active(self) -> bool:
        phase = int(self._source.info.data.scoring.scoringInfo.mGamePhase)
        return bool(self._source.info.data.telemetry.playerHasVehicle and phase not in (0, 7, 8, 9))
    def paused(self) -> bool: return self._source.info.data.scoring.scoringInfo.mGamePhase == 9
    def version(self) -> str: return str(self._source.info.data.generic.gameVersion)


class LMULapProvider(Lap):
    def __init__(self, source: LMUSource) -> None: self._source = source
    def _scor(self, index: int | None):
        idx = self._source.info.data.telemetry.playerVehicleIdx if index is None else index
        return self._source.info.data.scoring.vehScoringInfo[idx]
    def _telem(self, index: int | None):
        idx = self._source.info.data.telemetry.playerVehicleIdx if index is None else index
        return self._source.info.data.telemetry.telemInfo[idx]
    def current_lap(self, index: int | None = None) -> int: return int(self._telem(index).mLapNumber)
    def completed_laps(self, index: int | None = None) -> int: return int(self._scor(index).mTotalLaps)
    def track_length(self) -> float: return float(self._source.info.data.scoring.scoringInfo.mLapDist)
    def lap_distance(self, index: int | None = None) -> float: return float(self._scor(index).mLapDist)
    def lap_progress(self, index: int | None = None) -> float:
        length = self.track_length()
        return self.lap_distance(index) / length if length > 0 else 0.0
    def current_sector(self, index: int | None = None) -> int: return {0: 2, 1: 0, 2: 1}.get(int(self._scor(index).mSector), 0)


class LMUSessionProvider(Session):
    def __init__(self, source: LMUSource) -> None: self._source = source
    def _si(self): return self._source.info.data.scoring.scoringInfo
    def track_name(self) -> str: return decode_bytes(self._si().mTrackName)
    def session_time_elapsed(self) -> float: return float(self._si().mCurrentET)
    def session_time_left(self) -> float: return float(self._si().mEndET - self._si().mCurrentET)
    def session_kind(self) -> int:
        raw = int(self._si().mSession)
        if raw == 0: return 0
        if 1 <= raw <= 4: return 1
        if 5 <= raw <= 8: return 2
        if raw == 9: return 3
        return 4
    def is_race_session(self) -> bool: return self.session_kind() == 4
    def track_temperature(self) -> float: return float(self._si().mTrackTemp)
    def ambient_temperature(self) -> float: return float(self._si().mAmbientTemp)
    def raininess(self) -> float: return float(self._si().mRaining)
    def weather_forecast(self): return ()


class LMUTimingProvider(Timing):
    def __init__(self, source: LMUSource) -> None: self._source = source
    def _scor(self, index: int | None):
        idx = self._source.info.data.telemetry.playerVehicleIdx if index is None else index
        return self._source.info.data.scoring.vehScoringInfo[idx]
    def current_laptime(self, index: int | None = None) -> float: return float(self._scor(index).mTimeIntoLap)
    def last_laptime(self, index: int | None = None) -> float: return float(self._scor(index).mLastLapTime)
    def best_laptime(self, index: int | None = None) -> float: return float(self._scor(index).mBestLapTime)
    def current_sector1(self, index: int | None = None) -> float: return float(self._scor(index).mCurSector1)
    def current_sector2(self, index: int | None = None) -> float: return float(self._scor(index).mCurSector2)
    def last_sector1(self, index: int | None = None) -> float: return float(self._scor(index).mLastSector1)
    def last_sector2(self, index: int | None = None) -> float: return float(self._scor(index).mLastSector2)
    def best_sector1(self, index: int | None = None) -> float: return float(self._scor(index).mBestSector1)
    def best_sector2(self, index: int | None = None) -> float: return float(self._scor(index).mBestSector2)
    def gap_to_leader(self, index: int | None = None) -> float: return float(self._scor(index).mTimeBehindLeader)


class LMUBrakeProvider(Brake):
    def __init__(self, source: LMUSource) -> None: self._source = source
    def _wheels(self, index: int | None):
        idx = self._source.info.data.telemetry.playerVehicleIdx if index is None else index
        return self._source.info.data.telemetry.telemInfo[idx].mWheels
    def bias_front(self, index: int | None = None) -> float:
        idx = self._source.info.data.telemetry.playerVehicleIdx if index is None else index
        return 1.0 - float(self._source.info.data.telemetry.telemInfo[idx].mRearBrakeBias)
    def pressure(self, index: int | None = None, scale: float = 1) -> tuple[float, ...]:
        wheels = self._wheels(index)
        return tuple(float(wheels[i].mBrakePressure) * scale for i in range(4))
    def temperature(self, index: int | None = None) -> tuple[float, ...]:
        wheels = self._wheels(index)
        return tuple(float(wheels[i].mBrakeTemp) - _KELVIN for i in range(4))
    def wear(self, index: int | None = None) -> tuple[float, ...]:
        wheels = self._wheels(index)
        return tuple(float(wheels[i].mWear) for i in range(4))


class LMUElectricMotorProvider(ElectricMotor):
    def __init__(self, source: LMUSource) -> None: self._source = source
    def _telem(self, index: int | None):
        idx = self._source.info.data.telemetry.playerVehicleIdx if index is None else index
        return self._source.info.data.telemetry.telemInfo[idx]
    def state(self, index: int | None = None) -> int: return int(self._telem(index).mElectricBoostMotorState)
    def battery_charge(self, index: int | None = None) -> float: return float(self._telem(index).mBatteryChargeFraction)
    def rpm(self, index: int | None = None) -> float: return float(self._telem(index).mElectricBoostMotorRPM)
    def torque(self, index: int | None = None) -> float: return float(self._telem(index).mElectricBoostMotorTorque)
    def motor_temperature(self, index: int | None = None) -> float: return float(self._telem(index).mElectricBoostMotorTemperature)
    def water_temperature(self, index: int | None = None) -> float: return float(self._telem(index).mElectricBoostWaterTemperature)


class LMUEngineProvider(Engine):
    def __init__(self, source: LMUSource) -> None: self._source = source
    def _telem(self, index: int | None):
        idx = self._source.info.data.telemetry.playerVehicleIdx if index is None else index
        return self._source.info.data.telemetry.telemInfo[idx]
    def gear(self, index: int | None = None) -> int: return int(self._telem(index).mGear)
    def gear_max(self, index: int | None = None) -> int: return int(self._telem(index).mMaxGears)
    def rpm(self, index: int | None = None) -> float: return float(self._telem(index).mEngineRPM)
    def rpm_max(self, index: int | None = None) -> float: return float(self._telem(index).mEngineMaxRPM)
    def torque(self, index: int | None = None) -> float: return float(self._telem(index).mEngineTorque)
    def turbo(self, index: int | None = None) -> float: return float(self._telem(index).mTurboBoostPressure)
    def oil_temperature(self, index: int | None = None) -> float: return float(self._telem(index).mEngineOilTemp)
    def water_temperature(self, index: int | None = None) -> float: return float(self._telem(index).mEngineWaterTemp)


class LMUInputsProvider(Inputs):
    def __init__(self, source: LMUSource) -> None: self._source = source
    def _telem(self):
        idx = self._source.info.data.telemetry.playerVehicleIdx
        return self._source.info.data.telemetry.telemInfo[idx]
    def throttle(self, index: int | None = None) -> float: return float(self._telem().mFilteredThrottle)
    def throttle_raw(self, index: int | None = None) -> float: return float(self._telem().mUnfilteredThrottle)
    def brake(self, index: int | None = None) -> float: return float(self._telem().mFilteredBrake)
    def brake_raw(self, index: int | None = None) -> float: return float(self._telem().mUnfilteredBrake)
    def clutch(self, index: int | None = None) -> float: return float(self._telem().mFilteredClutch)
    def steering(self, index: int | None = None) -> float: return float(self._telem().mFilteredSteering)
    def steering_raw(self, index: int | None = None) -> float: return float(self._telem().mUnfilteredSteering)
    def force_feedback(self) -> float: return float(self._source.info.data.generic.FFBTorque)


class LMUSwitchProvider(Switch):
    def __init__(self, source: LMUSource) -> None: self._source = source
    def _telem(self, index: int | None):
        idx = self._source.info.data.telemetry.playerVehicleIdx if index is None else index
        return self._source.info.data.telemetry.telemInfo[idx]
    def headlights(self, index: int | None = None) -> int: return int(self._telem(index).mHeadlights)
    def speed_limiter(self, index: int | None = None) -> int: return int(self._telem(index).mSpeedLimiter)
    def drs_status(self, index: int | None = None) -> int:
        telem = self._telem(index)
        status = int(telem.mRearFlapLegalStatus)
        if status == 1:
            return 1
        if status == 2:
            return 3 if int(telem.mRearFlapActivated) else 2
        return 0


class LMUVehicleProvider(Vehicle):
    def __init__(self, source: LMUSource) -> None: self._source = source
    def _scor(self, index: int | None):
        idx = self._source.info.data.telemetry.playerVehicleIdx if index is None else index
        return self._source.info.data.scoring.vehScoringInfo[idx]
    def _telem(self, index: int | None):
        idx = self._source.info.data.telemetry.playerVehicleIdx if index is None else index
        return self._source.info.data.telemetry.telemInfo[idx]
    def player_index(self) -> int: return int(self._source.info.data.telemetry.playerVehicleIdx)
    def is_player(self, index: int = 0) -> bool: return index == self.player_index()
    def total_vehicles(self) -> int: return int(self._source.info.data.scoring.scoringInfo.mNumVehicles)
    def driver_name(self, index: int | None = None) -> str: return decode_bytes(self._scor(index).mDriverName)
    def vehicle_name(self, index: int | None = None) -> str: return decode_bytes(self._telem(index).mVehicleName)
    def class_name(self, index: int | None = None) -> str: return decode_bytes(self._scor(index).mVehicleClass)
    def place(self, index: int | None = None) -> int: return int(self._scor(index).mPlace)
    def in_pits(self, index: int | None = None) -> bool: return bool(self._scor(index).mInPits)
    def fuel(self, index: int | None = None) -> float: return float(self._telem(index).mFuel)
    def speed(self, index: int | None = None) -> float:
        velocity = self._telem(index).mLocalVel
        return math.sqrt(velocity.x ** 2 + velocity.y ** 2 + velocity.z ** 2)
    def position_xyz(self, index: int | None = None) -> tuple[float, float, float]:
        pos = self._telem(index).mPos
        return float(pos.x), float(pos.y), float(pos.z)


class LMUTyreProvider(Tyre):
    def __init__(self, source: LMUSource) -> None: self._source = source
    def _wheels(self, index: int | None):
        idx = self._source.info.data.telemetry.playerVehicleIdx if index is None else index
        return self._source.info.data.telemetry.telemInfo[idx].mWheels
    def compound(self, index: int | None = None) -> tuple[int, int]:
        idx = self._source.info.data.telemetry.playerVehicleIdx if index is None else index
        telem = self._source.info.data.telemetry.telemInfo[idx]
        return int(telem.mFrontTireCompoundIndex), int(telem.mRearTireCompoundIndex)
    def compound_name(self, index: int | None = None) -> tuple[str, str]:
        idx = self._source.info.data.telemetry.playerVehicleIdx if index is None else index
        telem = self._source.info.data.telemetry.telemInfo[idx]
        return decode_bytes(telem.mFrontTireCompoundName), decode_bytes(telem.mRearTireCompoundName)
    def surface_temperature(self, index: int | None = None) -> tuple[float, ...]:
        wheels = self._wheels(index)
        return tuple(float(wheels[i].mTemperature[1]) - _KELVIN for i in range(4))
    def inner_temperature(self, index: int | None = None) -> tuple[float, ...]:
        wheels = self._wheels(index)
        return tuple(float(wheels[i].mTireCarcassTemperature) - _KELVIN for i in range(4))
    def pressure(self, index: int | None = None) -> tuple[float, ...]:
        wheels = self._wheels(index)
        return tuple(float(wheels[i].mPressure) for i in range(4))
    def wear(self, index: int | None = None) -> tuple[float, ...]:
        wheels = self._wheels(index)
        return tuple(float(wheels[i].mWear) for i in range(4))
    def load(self, index: int | None = None) -> tuple[float, ...]:
        wheels = self._wheels(index)
        return tuple(float(wheels[i].mTireLoad) for i in range(4))


class LMUWheelProvider(Wheel):
    def __init__(self, source: LMUSource) -> None: self._source = source
    def _wheels(self, index: int | None):
        idx = self._source.info.data.telemetry.playerVehicleIdx if index is None else index
        return self._source.info.data.telemetry.telemInfo[idx].mWheels
    def camber(self, index: int | None = None) -> tuple[float, ...]:
        wheels = self._wheels(index)
        return tuple(float(wheels[i].mCamber) for i in range(4))
    def rotation(self, index: int | None = None) -> tuple[float, ...]:
        wheels = self._wheels(index)
        return tuple(float(wheels[i].mRotation) for i in range(4))
    def ride_height(self, index: int | None = None) -> tuple[float, ...]:
        wheels = self._wheels(index)
        return tuple(float(wheels[i].mRideHeight) * 1000 for i in range(4))
    def suspension_deflection(self, index: int | None = None) -> tuple[float, ...]:
        wheels = self._wheels(index)
        return tuple(float(wheels[i].mSuspensionDeflection) * 1000 for i in range(4))


class LMURealConnector:
    """Shared-memory composition layer for the raw LMU source capabilities."""

    def __init__(self) -> None:
        self._source = LMUSource()
        self._state = LMUStateProvider(self._source)
        self._brake = LMUBrakeProvider(self._source)
        self._electric_motor = LMUElectricMotorProvider(self._source)
        self._engine = LMUEngineProvider(self._source)
        self._inputs = LMUInputsProvider(self._source)
        self._lap = LMULapProvider(self._source)
        self._session = LMUSessionProvider(self._source)
        self._switch = LMUSwitchProvider(self._source)
        self._timing = LMUTimingProvider(self._source)
        self._tyre = LMUTyreProvider(self._source)
        self._vehicle = LMUVehicleProvider(self._source)
        self._wheel = LMUWheelProvider(self._source)

    def open(self) -> None: self._source.open()
    def close(self) -> None: self._source.close()
    def update(self) -> None: self._source.update()
    @property
    def state(self): return self._state
    @property
    def brake(self): return self._brake
    @property
    def electric_motor(self): return self._electric_motor
    @property
    def engine(self): return self._engine
    @property
    def inputs(self): return self._inputs
    @property
    def lap(self): return self._lap
    @property
    def session(self): return self._session
    @property
    def switch(self): return self._switch
    @property
    def timing(self): return self._timing
    @property
    def tyre(self): return self._tyre
    @property
    def vehicle(self): return self._vehicle
    @property
    def wheel(self): return self._wheel
