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

"""rFactor 2 telemetry reader and capability implementations."""

from __future__ import annotations

import math

from ...shared_memory.rFactor2 import RF2Info, bytes_to_str, number_or_zero
from ...contracts.telemetry import Brake, ElectricMotor, Engine, Inputs, Lap, Opponents, Session, State, Switch, TelemetryReader, Timing, Track, Tyre, Vehicle, WeatherNode, Wheel


class _RF2State(State):
    def __init__(self, info: RF2Info) -> None: self._info = info
    def active(self) -> bool: return self._info.isActive
    def paused(self) -> bool: return self._info.isPaused
    def version(self) -> str:
        version = bytes_to_str(self._info.rf2Ext.mVersion)
        return version if version else "unknown"


class _RF2Brake(Brake):
    def __init__(self, info: RF2Info) -> None: self._info = info
    def bias_front(self, index: int | None = None) -> float: return 1.0 - number_or_zero(self._info.rf2TeleVeh(index).mRearBrakeBias)
    def pressure(self, index: int | None = None, scale: float = 1) -> tuple[float, ...]:
        wheels = self._info.rf2TeleVeh(index).mWheels
        return tuple(number_or_zero(wheels[i].mBrakePressure) * scale for i in range(4))
    def temperature(self, index: int | None = None) -> tuple[float, ...]:
        wheels = self._info.rf2TeleVeh(index).mWheels
        return tuple(number_or_zero(wheels[i].mBrakeTemp) - 273.15 for i in range(4))
    def wear(self, index: int | None = None) -> tuple[float, ...]:
        wheels = self._info.rf2TeleVeh(index).mWheels
        return tuple(number_or_zero(wheels[i].mWear) for i in range(4))


class _RF2ElectricMotor(ElectricMotor):
    def __init__(self, info: RF2Info) -> None: self._info = info
    def state(self, index: int | None = None) -> int: return int(self._info.rf2TeleVeh(index).mElectricBoostMotorState)
    def battery_charge(self, index: int | None = None) -> float: return number_or_zero(self._info.rf2TeleVeh(index).mBatteryChargeFraction)
    def rpm(self, index: int | None = None) -> float: return number_or_zero(self._info.rf2TeleVeh(index).mElectricBoostMotorRPM)
    def torque(self, index: int | None = None) -> float: return number_or_zero(self._info.rf2TeleVeh(index).mElectricBoostMotorTorque)
    def motor_temperature(self, index: int | None = None) -> float: return number_or_zero(self._info.rf2TeleVeh(index).mElectricBoostMotorTemperature)
    def water_temperature(self, index: int | None = None) -> float: return number_or_zero(self._info.rf2TeleVeh(index).mElectricBoostWaterTemperature)


class _RF2Engine(Engine):
    def __init__(self, info: RF2Info) -> None: self._info = info
    def gear(self, index: int | None = None) -> int: return int(self._info.rf2TeleVeh(index).mGear)
    def gear_max(self, index: int | None = None) -> int: return int(self._info.rf2TeleVeh(index).mMaxGears)
    def rpm(self, index: int | None = None) -> float: return number_or_zero(self._info.rf2TeleVeh(index).mEngineRPM)
    def rpm_max(self, index: int | None = None) -> float: return number_or_zero(self._info.rf2TeleVeh(index).mEngineMaxRPM)
    def torque(self, index: int | None = None) -> float: return number_or_zero(self._info.rf2TeleVeh(index).mEngineTorque)
    def turbo(self, index: int | None = None) -> float: return number_or_zero(self._info.rf2TeleVeh(index).mTurboBoostPressure)
    def oil_temperature(self, index: int | None = None) -> float: return number_or_zero(self._info.rf2TeleVeh(index).mEngineOilTemp)
    def water_temperature(self, index: int | None = None) -> float: return number_or_zero(self._info.rf2TeleVeh(index).mEngineWaterTemp)


class _RF2Inputs(Inputs):
    def __init__(self, info: RF2Info) -> None: self._info = info
    def throttle(self, index: int | None = None) -> float: return number_or_zero(self._info.rf2TeleVeh(index).mFilteredThrottle)
    def throttle_raw(self, index: int | None = None) -> float: return number_or_zero(self._info.rf2TeleVeh(index).mUnfilteredThrottle)
    def brake(self, index: int | None = None) -> float: return number_or_zero(self._info.rf2TeleVeh(index).mFilteredBrake)
    def brake_raw(self, index: int | None = None) -> float: return number_or_zero(self._info.rf2TeleVeh(index).mUnfilteredBrake)
    def clutch(self, index: int | None = None) -> float: return number_or_zero(self._info.rf2TeleVeh(index).mFilteredClutch)
    def steering(self, index: int | None = None) -> float: return number_or_zero(self._info.rf2TeleVeh(index).mFilteredSteering)
    def steering_raw(self, index: int | None = None) -> float: return number_or_zero(self._info.rf2TeleVeh(index).mUnfilteredSteering)
    def force_feedback(self) -> float: return number_or_zero(self._info.rf2Ffb.mForceValue)


class _RF2Lap(Lap):
    def __init__(self, info: RF2Info) -> None: self._info = info
    def current_lap(self, index: int | None = None) -> int: return int(self._info.rf2TeleVeh(index).mLapNumber)
    def completed_laps(self, index: int | None = None) -> int: return int(self._info.rf2ScorVeh(index).mTotalLaps)
    def track_length(self) -> float: return number_or_zero(self._info.rf2ScorInfo.mLapDist)
    def lap_distance(self, index: int | None = None) -> float: return number_or_zero(self._info.rf2ScorVeh(index).mLapDist)
    def lap_progress(self, index: int | None = None) -> float:
        length = self.track_length()
        return self.lap_distance(index) / length if length > 0 else 0.0
    def current_sector(self, index: int | None = None) -> int:
        sector = int(self._info.rf2ScorVeh(index).mSector)
        return 2 if sector == 0 else 0 if sector == 1 else 1


class _RF2Session(Session):
    def __init__(self, info: RF2Info) -> None: self._info = info
    def track_name(self) -> str: return bytes_to_str(self._info.rf2ScorInfo.mTrackName)
    def session_time_elapsed(self) -> float: return number_or_zero(self._info.rf2ScorInfo.mCurrentET)
    def session_time_left(self) -> float:
        scor = self._info.rf2ScorInfo
        return number_or_zero(scor.mEndET - scor.mCurrentET)
    def session_kind(self) -> int:
        session = int(self._info.rf2ScorInfo.mSession)
        if session >= 10: return 4
        if session == 9: return 3
        if session >= 5: return 2
        if session >= 1: return 1
        return 0
    def is_race_session(self) -> bool: return self.session_kind() == 4
    def track_temperature(self) -> float: return number_or_zero(self._info.rf2ScorInfo.mTrackTemp)
    def ambient_temperature(self) -> float: return number_or_zero(self._info.rf2ScorInfo.mAmbientTemp)
    def raininess(self) -> float: return number_or_zero(self._info.rf2ScorInfo.mRaining)
    def weather_forecast(self) -> tuple[WeatherNode, ...]: return ()


class _RF2Switch(Switch):
    def __init__(self, info: RF2Info) -> None: self._info = info
    def headlights(self, index: int | None = None) -> int: return int(self._info.rf2TeleVeh(index).mHeadlights)
    def speed_limiter(self, index: int | None = None) -> int: return int(self._info.rf2TeleVeh(index).mSpeedLimiter)
    def drs_status(self, index: int | None = None) -> int:
        tele = self._info.rf2TeleVeh(index)
        status = int(tele.mRearFlapLegalStatus)
        if status == 1: return 1
        if status == 2: return 3 if tele.mRearFlapActivated else 2
        return 0


class _RF2Track(Track):
    def __init__(self, lap: _RF2Lap, session: _RF2Session) -> None:
        self._lap = lap
        self._session = session
    def name(self) -> str: return self._session.track_name()
    def length(self) -> float: return self._lap.track_length()
    def temperature(self) -> float: return self._session.track_temperature()
    def ambient_temperature(self) -> float: return self._session.ambient_temperature()
    def raininess(self) -> float: return self._session.raininess()


class _RF2Timing(Timing):
    def __init__(self, info: RF2Info) -> None: self._info = info
    def current_laptime(self, index: int | None = None) -> float:
        tele = self._info.rf2TeleVeh(index)
        return number_or_zero(tele.mElapsedTime - tele.mLapStartET)
    def last_laptime(self, index: int | None = None) -> float: return number_or_zero(self._info.rf2ScorVeh(index).mLastLapTime)
    def best_laptime(self, index: int | None = None) -> float: return number_or_zero(self._info.rf2ScorVeh(index).mBestLapTime)
    def current_sector1(self, index: int | None = None) -> float: return number_or_zero(self._info.rf2ScorVeh(index).mCurSector1)
    def current_sector2(self, index: int | None = None) -> float: return number_or_zero(self._info.rf2ScorVeh(index).mCurSector2)
    def last_sector1(self, index: int | None = None) -> float: return number_or_zero(self._info.rf2ScorVeh(index).mLastSector1)
    def last_sector2(self, index: int | None = None) -> float: return number_or_zero(self._info.rf2ScorVeh(index).mLastSector2)
    def best_sector1(self, index: int | None = None) -> float: return number_or_zero(self._info.rf2ScorVeh(index).mBestSector1)
    def best_sector2(self, index: int | None = None) -> float: return number_or_zero(self._info.rf2ScorVeh(index).mBestSector2)
    def gap_to_leader(self, index: int | None = None) -> float: return number_or_zero(self._info.rf2ScorVeh(index).mTimeBehindLeader)


class _RF2Tyre(Tyre):
    def __init__(self, info: RF2Info) -> None: self._info = info
    def compound(self, index: int | None = None) -> tuple[int, int]: return (0, 0)
    def compound_name(self, index: int | None = None) -> tuple[str, str]: return ("Unknown", "Unknown")
    def surface_temperature(self, index: int | None = None) -> tuple[float, ...]:
        wheels = self._info.rf2TeleVeh(index).mWheels
        return tuple(number_or_zero(wheels[i].mTemperature[1]) - 273.15 for i in range(4))
    def inner_temperature(self, index: int | None = None) -> tuple[float, ...]:
        wheels = self._info.rf2TeleVeh(index).mWheels
        return tuple(number_or_zero(wheels[i].mTireCarcassTemperature) - 273.15 for i in range(4))
    def pressure(self, index: int | None = None) -> tuple[float, ...]:
        wheels = self._info.rf2TeleVeh(index).mWheels
        return tuple(number_or_zero(wheels[i].mPressure) for i in range(4))
    def wear(self, index: int | None = None) -> tuple[float, ...]:
        wheels = self._info.rf2TeleVeh(index).mWheels
        return tuple(number_or_zero(wheels[i].mWear) for i in range(4))
    def load(self, index: int | None = None) -> tuple[float, ...]:
        wheels = self._info.rf2TeleVeh(index).mWheels
        return tuple(number_or_zero(wheels[i].mTireLoad) for i in range(4))


class _RF2Vehicle(Vehicle):
    def __init__(self, info: RF2Info) -> None: self._info = info
    def player_index(self) -> int: return self._info.playerIndex
    def is_player(self, index: int = 0) -> bool: return self._info.playerIndex == index
    def total_vehicles(self) -> int: return int(self._info.rf2ScorInfo.mNumVehicles)
    def driver_name(self, index: int | None = None) -> str: return bytes_to_str(self._info.rf2ScorVeh(index).mDriverName)
    def vehicle_name(self, index: int | None = None) -> str: return bytes_to_str(self._info.rf2ScorVeh(index).mVehicleName)
    def class_name(self, index: int | None = None) -> str: return bytes_to_str(self._info.rf2ScorVeh(index).mVehicleClass)
    def place(self, index: int | None = None) -> int: return int(self._info.rf2ScorVeh(index).mPlace)
    def in_pits(self, index: int | None = None) -> bool: return bool(self._info.rf2ScorVeh(index).mInPits)
    def fuel(self, index: int | None = None) -> float: return number_or_zero(self._info.rf2TeleVeh(index).mFuel)
    def speed(self, index: int | None = None) -> float:
        vel = self._info.rf2TeleVeh(index).mLocalVel
        x = number_or_zero(vel.x)
        y = number_or_zero(vel.y)
        z = number_or_zero(vel.z)
        return math.sqrt(x * x + y * y + z * z)
    def position_xyz(self, index: int | None = None) -> tuple[float, float, float]:
        pos = self._info.rf2TeleVeh(index).mPos
        return (number_or_zero(pos.x), number_or_zero(pos.y), number_or_zero(pos.z))


class _RF2Opponents(Opponents):
    def __init__(self, vehicle: _RF2Vehicle, lap: _RF2Lap, timing: _RF2Timing) -> None:
        self._vehicle = vehicle
        self._lap = lap
        self._timing = timing
    def total(self) -> int: return self._vehicle.total_vehicles()
    def is_player(self, index: int) -> bool: return self._vehicle.is_player(index)
    def driver_name(self, index: int) -> str: return self._vehicle.driver_name(index)
    def vehicle_name(self, index: int) -> str: return self._vehicle.vehicle_name(index)
    def class_name(self, index: int) -> str: return self._vehicle.class_name(index)
    def place(self, index: int) -> int: return self._vehicle.place(index)
    def lap_distance(self, index: int) -> float: return self._lap.lap_distance(index)
    def speed(self, index: int) -> float: return self._vehicle.speed(index)
    def in_pits(self, index: int) -> bool: return self._vehicle.in_pits(index)
    def gap_to_leader(self, index: int) -> float: return self._timing.gap_to_leader(index)


class _RF2Wheel(Wheel):
    def __init__(self, info: RF2Info) -> None: self._info = info
    def camber(self, index: int | None = None) -> tuple[float, ...]:
        wheels = self._info.rf2TeleVeh(index).mWheels
        return tuple(number_or_zero(wheels[i].mCamber) for i in range(4))
    def rotation(self, index: int | None = None) -> tuple[float, ...]:
        wheels = self._info.rf2TeleVeh(index).mWheels
        return tuple(number_or_zero(wheels[i].mRotation) for i in range(4))
    def ride_height(self, index: int | None = None) -> tuple[float, ...]:
        wheels = self._info.rf2TeleVeh(index).mWheels
        return tuple(number_or_zero(wheels[i].mRideHeight) * 1000 for i in range(4))
    def suspension_deflection(self, index: int | None = None) -> tuple[float, ...]:
        wheels = self._info.rf2TeleVeh(index).mWheels
        return tuple(number_or_zero(wheels[i].mSuspensionDeflection) * 1000 for i in range(4))


class RF2TelemetryReader(TelemetryReader):
    """Telemetry reader over the synchronous RF2 shared-memory runtime."""

    def __init__(self) -> None:
        self._info = RF2Info()
        self._state = _RF2State(self._info)
        self._brake = _RF2Brake(self._info)
        self._electric_motor = _RF2ElectricMotor(self._info)
        self._engine = _RF2Engine(self._info)
        self._inputs = _RF2Inputs(self._info)
        self._lap = _RF2Lap(self._info)
        self._session = _RF2Session(self._info)
        self._switch = _RF2Switch(self._info)
        self._timing = _RF2Timing(self._info)
        self._tyre = _RF2Tyre(self._info)
        self._vehicle = _RF2Vehicle(self._info)
        self._wheel = _RF2Wheel(self._info)
        self._track = _RF2Track(self._lap, self._session)
        self._opponents = _RF2Opponents(self._vehicle, self._lap, self._timing)

    def open(self) -> None: self._info.open()
    def close(self) -> None: self._info.close()
    def update(self) -> None: self._info.update()
    def raw_snapshot(self) -> list[tuple[str, str]]: return self._info.raw_snapshot()
    def memory_snapshot(self) -> list[tuple[str, str]]: return self._info.memory_snapshot()
    @property
    def state(self) -> State: return self._state
    @property
    def brake(self) -> Brake: return self._brake
    @property
    def electric_motor(self) -> ElectricMotor: return self._electric_motor
    @property
    def engine(self) -> Engine: return self._engine
    @property
    def inputs(self) -> Inputs: return self._inputs
    @property
    def lap(self) -> Lap: return self._lap
    @property
    def session(self) -> Session: return self._session
    @property
    def track(self) -> Track: return self._track
    @property
    def opponents(self) -> Opponents: return self._opponents
    @property
    def switch(self) -> Switch: return self._switch
    @property
    def timing(self) -> Timing: return self._timing
    @property
    def tyre(self) -> Tyre: return self._tyre
    @property
    def vehicle(self) -> Vehicle: return self._vehicle
    @property
    def wheel(self) -> Wheel: return self._wheel
