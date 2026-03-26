#  TinyUI
"""LMU vehicle-domain providers."""

from __future__ import annotations

import math

from .reader import Brake, Engine, Inputs, Switch, Vehicle, Wheel

from .shared import _KELVIN, decode_bytes
from .source import LMUSource


class LMUBrakeProvider(Brake):
    def __init__(self, source: LMUSource) -> None:
        self._source = source

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


class LMUEngineProvider(Engine):
    def __init__(self, source: LMUSource) -> None:
        self._source = source

    def _telem(self, index: int | None):
        idx = self._source.info.data.telemetry.playerVehicleIdx if index is None else index
        return self._source.info.data.telemetry.telemInfo[idx]

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


class LMUInputsProvider(Inputs):
    def __init__(self, source: LMUSource) -> None:
        self._source = source

    def _telem(self):
        idx = self._source.info.data.telemetry.playerVehicleIdx
        return self._source.info.data.telemetry.telemInfo[idx]

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
        return float(self._source.info.data.generic.FFBTorque)


class LMUSwitchProvider(Switch):
    def __init__(self, source: LMUSource) -> None:
        self._source = source

    def _telem(self, index: int | None):
        idx = self._source.info.data.telemetry.playerVehicleIdx if index is None else index
        return self._source.info.data.telemetry.telemInfo[idx]

    def headlights(self, index: int | None = None) -> int:
        return int(self._telem(index).mHeadlights)

    def speed_limiter(self, index: int | None = None) -> int:
        return int(self._telem(index).mSpeedLimiter)

    def drs_status(self, index: int | None = None) -> int:
        return 0


class LMUVehicleProvider(Vehicle):
    def __init__(self, source: LMUSource) -> None:
        self._source = source

    def _scor(self, index: int | None):
        idx = self._source.info.data.telemetry.playerVehicleIdx if index is None else index
        return self._source.info.data.scoring.vehScoringInfo[idx]

    def _telem(self, index: int | None):
        idx = self._source.info.data.telemetry.playerVehicleIdx if index is None else index
        return self._source.info.data.telemetry.telemInfo[idx]

    def player_index(self) -> int:
        return int(self._source.info.data.telemetry.playerVehicleIdx)

    def is_player(self, index: int = 0) -> bool:
        return index == self.player_index()

    def total_vehicles(self) -> int:
        return int(self._source.info.data.scoring.scoringInfo.mNumVehicles)

    def driver_name(self, index: int | None = None) -> str:
        return decode_bytes(self._scor(index).mDriverName)

    def vehicle_name(self, index: int | None = None) -> str:
        return decode_bytes(self._telem(index).mVehicleName)

    def class_name(self, index: int | None = None) -> str:
        return decode_bytes(self._scor(index).mVehicleClass)

    def place(self, index: int | None = None) -> int:
        return int(self._scor(index).mPlace)

    def in_pits(self, index: int | None = None) -> bool:
        return bool(self._scor(index).mInPits)

    def fuel(self, index: int | None = None) -> float:
        return float(self._telem(index).mFuel)

    def speed(self, index: int | None = None) -> float:
        velocity = self._telem(index).mLocalVel
        return math.sqrt(velocity.x ** 2 + velocity.y ** 2 + velocity.z ** 2)

    def position_xyz(self, index: int | None = None) -> tuple[float, float, float]:
        pos = self._telem(index).mPos
        return float(pos.x), float(pos.y), float(pos.z)


class LMUWheelProvider(Wheel):
    def __init__(self, source: LMUSource) -> None:
        self._source = source

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
