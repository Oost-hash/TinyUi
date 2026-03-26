#  TinyUI
"""LMU tyre-domain provider."""

from __future__ import annotations

from .reader import Tyre

from .shared import _KELVIN, decode_bytes
from .source import LMUSource


class LMUTyreProvider(Tyre):
    def __init__(self, source: LMUSource) -> None:
        self._source = source

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
