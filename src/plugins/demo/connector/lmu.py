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
"""LMU connector — wraps pyLMUSharedMemory and implements TelemetryReader.

Usage in a plugin:
    from plugins.demo.connector.lmu import LMUConnector

    connector = LMUConnector()
    connector.open()
    ctx.connector.register(connector)
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

# pyLMUSharedMemory lives as a submodule next to this file
_LIB = Path(__file__).parent.parent
if str(_LIB) not in sys.path:
    sys.path.insert(0, str(_LIB))

from pyLMUSharedMemory.lmu_mmap import MMapControl  # type: ignore[import]
from pyLMUSharedMemory import lmu_data               # type: ignore[import]
from pyLMUSharedMemory.lmu_data import LMUConstants  # type: ignore[import]

from tinycore.telemetry.reader import (
    Brake,
    ElectricMotor,
    Engine,
    Inputs,
    Lap,
    Session,
    State,
    Switch,
    TelemetryReader,
    Timing,
    Tyre,
    Vehicle,
    WeatherNode,
    Wheel,
)

_KELVIN = 273.15


def _decode(b: bytes) -> str:
    return b.rstrip(b"\x00").decode("utf-8", errors="replace")


# ---------------------------------------------------------------------------
# Sub-reader implementations
# ---------------------------------------------------------------------------

class _State(State):

    def __init__(self, info: MMapControl) -> None:
        self._info = info

    def active(self) -> bool:
        phase = int(self._info.data.scoring.scoringInfo.mGamePhase)
        # gamePhase: 0=before session, 7=stopped, 8=over, 9=paused
        # SME_ENTER/EXIT_REALTIME counters zijn gelijk in LMU — niet bruikbaar
        return bool(
            self._info.data.telemetry.playerHasVehicle
            and phase not in (0, 7, 8, 9)
        )

    def paused(self) -> bool:
        return self._info.data.scoring.scoringInfo.mGamePhase == 9

    def version(self) -> str:
        return str(self._info.data.generic.gameVersion)


class _Brake(Brake):

    def __init__(self, info: MMapControl) -> None:
        self._info = info

    def _player_idx(self) -> int:
        return self._info.data.telemetry.playerVehicleIdx

    def _wheels(self, index: int | None) -> lmu_data.LMUVehicleTelemetry:
        idx = self._player_idx() if index is None else index
        return self._info.data.telemetry.telemInfo[idx].mWheels

    def bias_front(self, index: int | None = None) -> float:
        idx = self._player_idx() if index is None else index
        # LMU exposes rear bias — invert to get front bias
        return 1.0 - float(self._info.data.telemetry.telemInfo[idx].mRearBrakeBias)

    def pressure(self, index: int | None = None, scale: float = 1) -> tuple[float, ...]:
        wheels = self._wheels(index)
        return tuple(float(wheels[i].mBrakePressure) * scale for i in range(4))

    def temperature(self, index: int | None = None) -> tuple[float, ...]:
        wheels = self._wheels(index)
        return tuple(float(wheels[i].mBrakeTemp) - _KELVIN for i in range(4))

    def wear(self, index: int | None = None) -> tuple[float, ...]:
        wheels = self._wheels(index)
        return tuple(float(wheels[i].mWear) for i in range(4))


class _ElectricMotor(ElectricMotor):
    """LMU has no hybrid data — returns neutral/zero values."""

    def state(self, index: int | None = None) -> int:
        return 0

    def battery_charge(self, index: int | None = None) -> float:
        return 0.0

    def rpm(self, index: int | None = None) -> float:
        return 0.0

    def torque(self, index: int | None = None) -> float:
        return 0.0

    def motor_temperature(self, index: int | None = None) -> float:
        return 0.0

    def water_temperature(self, index: int | None = None) -> float:
        return 0.0


class _Engine(Engine):

    def __init__(self, info: MMapControl) -> None:
        self._info = info

    def _telem(self, index: int | None) -> lmu_data.LMUVehicleTelemetry:
        idx = self._info.data.telemetry.playerVehicleIdx if index is None else index
        return self._info.data.telemetry.telemInfo[idx]

    def gear(self, index: int | None = None) -> int:
        return int(self._telem(index).mGear)

    def gear_max(self, index: int | None = None) -> int:
        return int(self._telem(index).mMaxGears)

    def rpm(self, index: int | None = None) -> float:
        return float(self._telem(index).mEngineRPM)

    def rpm_max(self, index: int | None = None) -> float:
        return float(self._telem(index).mEngineMaxRPM)

    def torque(self, index: int | None = None) -> float:
        return float(self._telem(index).mEngineTorque)

    def turbo(self, index: int | None = None) -> float:
        return float(self._telem(index).mTurboBoostPressure)

    def oil_temperature(self, index: int | None = None) -> float:
        return float(self._telem(index).mEngineOilTemp)

    def water_temperature(self, index: int | None = None) -> float:
        return float(self._telem(index).mEngineWaterTemp)


class _Inputs(Inputs):

    def __init__(self, info: MMapControl) -> None:
        self._info = info

    def _telem(self) -> lmu_data.LMUVehicleTelemetry:
        idx = self._info.data.telemetry.playerVehicleIdx
        return self._info.data.telemetry.telemInfo[idx]

    def throttle(self, index: int | None = None) -> float:
        return float(self._telem().mFilteredThrottle)

    def throttle_raw(self, index: int | None = None) -> float:
        return float(self._telem().mUnfilteredThrottle)

    def brake(self, index: int | None = None) -> float:
        return float(self._telem().mFilteredBrake)

    def brake_raw(self, index: int | None = None) -> float:
        return float(self._telem().mUnfilteredBrake)

    def clutch(self, index: int | None = None) -> float:
        return float(self._telem().mFilteredClutch)

    def steering(self, index: int | None = None) -> float:
        return float(self._telem().mFilteredSteering)

    def steering_raw(self, index: int | None = None) -> float:
        return float(self._telem().mUnfilteredSteering)

    def force_feedback(self) -> float:
        return float(self._info.data.generic.FFBTorque)


class _Lap(Lap):

    def __init__(self, info: MMapControl) -> None:
        self._info = info

    def _scor(self, index: int | None) -> lmu_data.LMUVehicleScoring:
        idx = self._info.data.telemetry.playerVehicleIdx if index is None else index
        return self._info.data.scoring.vehScoringInfo[idx]

    def number(self, index: int | None = None) -> int:
        return int(self._scor(index).mLapNumber)

    def completed_laps(self, index: int | None = None) -> int:
        return int(self._scor(index).mTotalLaps)

    def track_length(self) -> float:
        return float(self._info.data.scoring.scoringInfo.mLapDist)

    def distance(self, index: int | None = None) -> float:
        return float(self._scor(index).mLapDist)

    def progress(self, index: int | None = None) -> float:
        length = self.track_length()
        return self.distance(index) / length if length > 0 else 0.0

    def sector_index(self, index: int | None = None) -> int:
        # LMU: 0=S3, 1=S1, 2=S2 — remap to 0=S1, 1=S2, 2=S3
        raw = int(self._scor(index).mSector)
        return {0: 2, 1: 0, 2: 1}.get(raw, 0)


class _Session(Session):

    def __init__(self, info: MMapControl) -> None:
        self._info = info

    def _si(self) -> lmu_data.LMUScoringInfo:
        return self._info.data.scoring.scoringInfo

    def track_name(self) -> str:
        return _decode(self._si().mTrackName)

    def elapsed(self) -> float:
        return float(self._si().mCurrentET)

    def remaining(self) -> float:
        return float(self._si().mEndET - self._si().mCurrentET)

    def session_type(self) -> int:
        raw = int(self._si().mSession)
        if raw == 0:
            return 0   # test day
        if 1 <= raw <= 4:
            return 1   # practice
        if 5 <= raw <= 8:
            return 2   # qualify
        if raw == 9:
            return 3   # warmup
        return 4       # race

    def in_race(self) -> bool:
        return self.session_type() == 4

    def track_temperature(self) -> float:
        return float(self._si().mTrackTemp)

    def ambient_temperature(self) -> float:
        return float(self._si().mAmbientTemp)

    def raininess(self) -> float:
        return float(self._si().mRaining)

    def weather_forecast(self) -> tuple[WeatherNode, ...]:
        # LMU shared memory does not expose a forecast stream
        return ()


class _Switch(Switch):

    def __init__(self, info: MMapControl) -> None:
        self._info = info

    def _telem(self, index: int | None) -> lmu_data.LMUVehicleTelemetry:
        idx = self._info.data.telemetry.playerVehicleIdx if index is None else index
        return self._info.data.telemetry.telemInfo[idx]

    def headlights(self, index: int | None = None) -> int:
        return int(self._telem(index).mHeadlights)

    def speed_limiter(self, index: int | None = None) -> int:
        return int(self._telem(index).mSpeedLimiter)

    def drs_status(self, index: int | None = None) -> int:
        return 0   # LMU has no DRS


class _Timing(Timing):

    def __init__(self, info: MMapControl) -> None:
        self._info = info

    def _scor(self, index: int | None) -> lmu_data.LMUVehicleScoring:
        idx = self._info.data.telemetry.playerVehicleIdx if index is None else index
        return self._info.data.scoring.vehScoringInfo[idx]

    def current_laptime(self, index: int | None = None) -> float:
        return float(self._scor(index).mTimeIntoLap)

    def last_laptime(self, index: int | None = None) -> float:
        return float(self._scor(index).mLastLapTime)

    def best_laptime(self, index: int | None = None) -> float:
        return float(self._scor(index).mBestLapTime)

    def current_sector1(self, index: int | None = None) -> float:
        return float(self._scor(index).mCurSector1)

    def current_sector2(self, index: int | None = None) -> float:
        return float(self._scor(index).mCurSector2)

    def last_sector1(self, index: int | None = None) -> float:
        return float(self._scor(index).mLastSector1)

    def last_sector2(self, index: int | None = None) -> float:
        return float(self._scor(index).mLastSector2)

    def best_sector1(self, index: int | None = None) -> float:
        return float(self._scor(index).mBestSector1)

    def best_sector2(self, index: int | None = None) -> float:
        return float(self._scor(index).mBestSector2)

    def behind_leader(self, index: int | None = None) -> float:
        return float(self._scor(index).mTimeBehindLeader)


class _Tyre(Tyre):

    def __init__(self, info: MMapControl) -> None:
        self._info = info

    def _wheels(self, index: int | None) -> tuple:
        idx = self._info.data.telemetry.playerVehicleIdx if index is None else index
        return self._info.data.telemetry.telemInfo[idx].mWheels

    def _scor(self, index: int | None) -> lmu_data.LMUVehicleScoring:
        idx = self._info.data.telemetry.playerVehicleIdx if index is None else index
        return self._info.data.scoring.vehScoringInfo[idx]

    def compound(self, index: int | None = None) -> tuple[int, int]:
        idx = self._info.data.telemetry.playerVehicleIdx if index is None else index
        t = self._info.data.telemetry.telemInfo[idx]
        return (int(t.mFrontTireCompoundIndex), int(t.mRearTireCompoundIndex))

    def compound_name(self, index: int | None = None) -> tuple[str, str]:
        idx = self._info.data.telemetry.playerVehicleIdx if index is None else index
        t = self._info.data.telemetry.telemInfo[idx]
        return (_decode(t.mFrontTireCompoundName), _decode(t.mRearTireCompoundName))

    def surface_temperature(self, index: int | None = None) -> tuple[float, ...]:
        wheels = self._wheels(index)
        # mTemperature is [left, center, right] in Kelvin — return center
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


class _Vehicle(Vehicle):

    def __init__(self, info: MMapControl) -> None:
        self._info = info

    def _scor(self, index: int | None) -> lmu_data.LMUVehicleScoring:
        idx = self._info.data.telemetry.playerVehicleIdx if index is None else index
        return self._info.data.scoring.vehScoringInfo[idx]

    def _telem(self, index: int | None) -> lmu_data.LMUVehicleTelemetry:
        idx = self._info.data.telemetry.playerVehicleIdx if index is None else index
        return self._info.data.telemetry.telemInfo[idx]

    def player_index(self) -> int:
        return int(self._info.data.telemetry.playerVehicleIdx)

    def is_player(self, index: int = 0) -> bool:
        return index == self.player_index()

    def total_vehicles(self) -> int:
        return int(self._info.data.scoring.scoringInfo.mNumVehicles)

    def driver_name(self, index: int | None = None) -> str:
        return _decode(self._scor(index).mDriverName)

    def vehicle_name(self, index: int | None = None) -> str:
        return _decode(self._telem(index).mVehicleName)

    def class_name(self, index: int | None = None) -> str:
        return _decode(self._scor(index).mVehicleClass)

    def place(self, index: int | None = None) -> int:
        return int(self._scor(index).mPlace)

    def in_pits(self, index: int | None = None) -> bool:
        return bool(self._scor(index).mInPits)

    def fuel(self, index: int | None = None) -> float:
        return float(self._telem(index).mFuel)

    def speed(self, index: int | None = None) -> float:
        v = self._telem(index).mLocalVel
        return math.sqrt(v.x ** 2 + v.y ** 2 + v.z ** 2)

    def position_xyz(self, index: int | None = None) -> tuple[float, float, float]:
        p = self._telem(index).mPos
        return (float(p.x), float(p.y), float(p.z))


class _Wheel(Wheel):

    def __init__(self, info: MMapControl) -> None:
        self._info = info

    def _wheels(self, index: int | None) -> tuple:
        idx = self._info.data.telemetry.playerVehicleIdx if index is None else index
        return self._info.data.telemetry.telemInfo[idx].mWheels

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


# ---------------------------------------------------------------------------
# Top-level connector
# ---------------------------------------------------------------------------

class LMUConnector(TelemetryReader):
    """TelemetryReader implementation for Le Mans Ultimate / rFactor 2.

    Wraps pyLMUSharedMemory.MMapControl and implements the full
    TelemetryReader contract. Instantiate, call open(), then register
    via ctx.connector.register(connector).
    """

    def __init__(self) -> None:
        self._info = MMapControl(
            LMUConstants.LMU_SHARED_MEMORY_FILE,
            lmu_data.LMUObjectOut,
        )
        self._state          = _State(self._info)
        self._brake          = _Brake(self._info)
        self._electric_motor = _ElectricMotor()
        self._engine         = _Engine(self._info)
        self._inputs         = _Inputs(self._info)
        self._lap            = _Lap(self._info)
        self._session        = _Session(self._info)
        self._switch         = _Switch(self._info)
        self._timing         = _Timing(self._info)
        self._tyre           = _Tyre(self._info)
        self._vehicle        = _Vehicle(self._info)
        self._wheel          = _Wheel(self._info)

    def open(self) -> None:
        self._info.create()

    def close(self) -> None:
        self._info.close()

    def update(self) -> None:
        self._info.update()

    @property
    def state(self) -> State:
        return self._state

    @property
    def brake(self) -> Brake:
        return self._brake

    @property
    def electric_motor(self) -> ElectricMotor:
        return self._electric_motor

    @property
    def engine(self) -> Engine:
        return self._engine

    @property
    def inputs(self) -> Inputs:
        return self._inputs

    @property
    def lap(self) -> Lap:
        return self._lap

    @property
    def session(self) -> Session:
        return self._session

    @property
    def switch(self) -> Switch:
        return self._switch

    @property
    def timing(self) -> Timing:
        return self._timing

    @property
    def tyre(self) -> Tyre:
        return self._tyre

    @property
    def vehicle(self) -> Vehicle:
        return self._vehicle

    @property
    def wheel(self) -> Wheel:
        return self._wheel
