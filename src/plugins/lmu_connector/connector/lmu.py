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
"""LMU connector composition root.

The LMU connector is now composed from a shared LMU source plus domain
providers. This file only wires those pieces together.
"""

from __future__ import annotations

from tinycore.telemetry.reader import ElectricMotor, TelemetryReader

from .session import LMULapProvider, LMUSessionProvider, LMUStateProvider, LMUTimingProvider
from .source import LMUSource
from .tyre import LMUTyreProvider
from .vehicle import (
    LMUBrakeProvider,
    LMUEngineProvider,
    LMUInputsProvider,
    LMUSwitchProvider,
    LMUVehicleProvider,
    LMUWheelProvider,
)


class LMUElectricMotorProvider(ElectricMotor):
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


class LMUConnector(TelemetryReader):
    """Thin composition layer over LMU source and domain providers."""

    def __init__(self) -> None:
        self._source = LMUSource()
        self._state = LMUStateProvider(self._source)
        self._brake = LMUBrakeProvider(self._source)
        self._electric_motor = LMUElectricMotorProvider()
        self._engine = LMUEngineProvider(self._source)
        self._inputs = LMUInputsProvider(self._source)
        self._lap = LMULapProvider(self._source)
        self._session = LMUSessionProvider(self._source)
        self._switch = LMUSwitchProvider(self._source)
        self._timing = LMUTimingProvider(self._source)
        self._tyre = LMUTyreProvider(self._source)
        self._vehicle = LMUVehicleProvider(self._source)
        self._wheel = LMUWheelProvider(self._source)

    @property
    def source(self) -> LMUSource:
        """Shared LMU source used by all providers."""
        return self._source

    def open(self) -> None:
        self._source.open()

    def close(self) -> None:
        self._source.close()

    def update(self) -> None:
        self._source.update()

    @property
    def state(self):
        return self._state

    @property
    def brake(self):
        return self._brake

    @property
    def electric_motor(self):
        return self._electric_motor

    @property
    def engine(self):
        return self._engine

    @property
    def inputs(self):
        return self._inputs

    @property
    def lap(self):
        return self._lap

    @property
    def session(self):
        return self._session

    @property
    def switch(self):
        return self._switch

    @property
    def timing(self):
        return self._timing

    @property
    def tyre(self):
        return self._tyre

    @property
    def vehicle(self):
        return self._vehicle

    @property
    def wheel(self):
        return self._wheel
