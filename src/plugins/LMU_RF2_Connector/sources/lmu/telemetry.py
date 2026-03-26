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

"""LMU telemetry reader and capability extensions."""

from __future__ import annotations

from typing import cast

from ...shared_memory.LeMansUltimate import LMURealConnector

from ...contracts.telemetry import Brake, ElectricMotor, Engine, Inputs, Lap, Opponents, Session, State, Switch, TelemetryReader, Timing, Track, Tyre, Vehicle, Wheel


class _LMUTrack(Track):
    def __init__(self, lap: Lap, session: Session) -> None:
        self._lap = lap
        self._session = session

    def name(self) -> str: return self._session.track_name()
    def length(self) -> float: return self._lap.track_length()
    def temperature(self) -> float: return self._session.track_temperature()
    def ambient_temperature(self) -> float: return self._session.ambient_temperature()
    def raininess(self) -> float: return self._session.raininess()


class _LMUOpponents(Opponents):
    def __init__(self, vehicle: Vehicle, lap: Lap, timing: Timing) -> None:
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


class LMUTelemetryReader(TelemetryReader):
    """Thin wrapper around the existing LMU runtime with family extras."""

    def __init__(self) -> None:
        self._real = LMURealConnector()
        self._track = _LMUTrack(cast(Lap, self._real.lap), cast(Session, self._real.session))
        self._opponents = _LMUOpponents(cast(Vehicle, self._real.vehicle), cast(Lap, self._real.lap), cast(Timing, self._real.timing))

    def open(self) -> None: self._real.open()
    def close(self) -> None: self._real.close()
    def update(self) -> None: self._real.update()
    def raw_snapshot(self) -> list[tuple[str, str]]: return self._real.raw_snapshot()
    @property
    def state(self) -> State: return cast(State, self._real.state)
    @property
    def brake(self) -> Brake: return cast(Brake, self._real.brake)
    @property
    def electric_motor(self) -> ElectricMotor: return cast(ElectricMotor, self._real.electric_motor)
    @property
    def engine(self) -> Engine: return cast(Engine, self._real.engine)
    @property
    def inputs(self) -> Inputs: return cast(Inputs, self._real.inputs)
    @property
    def lap(self) -> Lap: return cast(Lap, self._real.lap)
    @property
    def session(self) -> Session: return cast(Session, self._real.session)
    @property
    def track(self) -> Track: return self._track
    @property
    def opponents(self) -> Opponents: return self._opponents
    @property
    def switch(self) -> Switch: return cast(Switch, self._real.switch)
    @property
    def timing(self) -> Timing: return cast(Timing, self._real.timing)
    @property
    def tyre(self) -> Tyre: return cast(Tyre, self._real.tyre)
    @property
    def vehicle(self) -> Vehicle: return cast(Vehicle, self._real.vehicle)
    @property
    def wheel(self) -> Wheel: return cast(Wheel, self._real.wheel)
