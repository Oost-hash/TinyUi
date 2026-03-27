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

"""Mock telemetry reader and capability implementations."""

from __future__ import annotations

import math

from .signals import Signal
from ...contracts.telemetry import Brake, ElectricMotor, Engine, Inputs, Lap, Opponents, Session, State, Switch, TelemetryReader, Timing, Track, Tyre, Vehicle, WeatherNode, Wheel


class _MockState(State):
    def active(self) -> bool: return True
    def paused(self) -> bool: return False
    def version(self) -> str: return "mock-telemetry-0.2"


class _MockBrake(Brake):
    def __init__(self, fuel: Signal) -> None: self._fuel = fuel
    def bias_front(self, index: int | None = None) -> float: return 0.58
    def pressure(self, index: int | None = None, scale: float = 1) -> tuple[float, ...]:
        base = 0.2 + (1.0 - self._fuel.value / max(self._fuel.maximum, 1.0)) * 0.6
        return tuple(base * scale for _ in range(4))
    def temperature(self, index: int | None = None) -> tuple[float, ...]: return (420.0, 428.0, 410.0, 417.0)
    def wear(self, index: int | None = None) -> tuple[float, ...]: return (0.94, 0.94, 0.96, 0.96)


class _MockElectricMotor(ElectricMotor):
    def state(self, index: int | None = None) -> int: return 0
    def battery_charge(self, index: int | None = None) -> float: return 0.0
    def rpm(self, index: int | None = None) -> float: return 0.0
    def torque(self, index: int | None = None) -> float: return 0.0
    def motor_temperature(self, index: int | None = None) -> float: return 0.0
    def water_temperature(self, index: int | None = None) -> float: return 0.0


class _MockEngine(Engine):
    def __init__(self, speed: Signal) -> None: self._speed = speed
    def gear(self, index: int | None = None) -> int: return min(6, max(1, int(self._speed.value // 45) + 1))
    def gear_max(self, index: int | None = None) -> int: return 6
    def rpm(self, index: int | None = None) -> float: return 2200.0 + self._speed.value * 45.0
    def rpm_max(self, index: int | None = None) -> float: return 8200.0
    def torque(self, index: int | None = None) -> float: return 410.0
    def turbo(self, index: int | None = None) -> float: return 0.0
    def oil_temperature(self, index: int | None = None) -> float: return 103.0
    def water_temperature(self, index: int | None = None) -> float: return 91.0


class _MockInputs(Inputs):
    def __init__(self, speed: Signal) -> None: self._speed = speed
    def throttle(self, index: int | None = None) -> float: return min(1.0, self._speed.value / max(self._speed.maximum, 1.0))
    def throttle_raw(self, index: int | None = None) -> float: return self.throttle(index)
    def brake(self, index: int | None = None) -> float: return max(0.0, 1.0 - self.throttle(index))
    def brake_raw(self, index: int | None = None) -> float: return self.brake(index)
    def clutch(self, index: int | None = None) -> float: return 0.0
    def steering(self, index: int | None = None) -> float: return math.sin(self._speed.value / 25.0) * 0.18
    def steering_raw(self, index: int | None = None) -> float: return self.steering(index)
    def force_feedback(self) -> float: return 0.35


class _MockLap(Lap):
    def __init__(self, speed: Signal) -> None:
        self._speed = speed
        self._track_length = 5412.0
    def current_lap(self, index: int | None = None) -> int: return 12
    def completed_laps(self, index: int | None = None) -> int: return 11
    def track_length(self) -> float: return self._track_length
    def lap_distance(self, index: int | None = None) -> float: return (self._speed.value * 19.0) % self._track_length
    def lap_progress(self, index: int | None = None) -> float: return self.lap_distance(index) / self._track_length
    def current_sector(self, index: int | None = None) -> int: return min(2, int(self.lap_progress(index) * 3))


class _MockSession(Session):
    def __init__(self, remaining: Signal, track_temp: Signal, ambient: Signal) -> None:
        self._remaining = remaining
        self._track_temp = track_temp
        self._ambient = ambient
    def track_name(self) -> str: return "Mock Circuit"
    def session_time_elapsed(self) -> float: return 5400.0 - self._remaining.value
    def session_time_left(self) -> float: return self._remaining.value
    def session_kind(self) -> int: return 4
    def is_race_session(self) -> bool: return True
    def track_temperature(self) -> float: return self._track_temp.value
    def ambient_temperature(self) -> float: return self._ambient.value
    def raininess(self) -> float: return 0.0
    def weather_forecast(self) -> tuple[WeatherNode, ...]: return ()


class _MockSwitch(Switch):
    def headlights(self, index: int | None = None) -> int: return 0
    def speed_limiter(self, index: int | None = None) -> int: return 0
    def drs_status(self, index: int | None = None) -> int: return 0


class _MockTrack(Track):
    def __init__(self, lap: _MockLap, session: _MockSession) -> None:
        self._lap = lap
        self._session = session
    def name(self) -> str: return self._session.track_name()
    def length(self) -> float: return self._lap.track_length()
    def temperature(self) -> float: return self._session.track_temperature()
    def ambient_temperature(self) -> float: return self._session.ambient_temperature()
    def raininess(self) -> float: return self._session.raininess()


class _MockTiming(Timing):
    def __init__(self, speed: Signal) -> None: self._speed = speed
    def current_laptime(self, index: int | None = None) -> float: return 73.0 + self._speed.value / 90.0
    def last_laptime(self, index: int | None = None) -> float: return 92.418
    def best_laptime(self, index: int | None = None) -> float: return 91.772
    def current_sector1(self, index: int | None = None) -> float: return 30.712
    def current_sector2(self, index: int | None = None) -> float: return 61.204
    def last_sector1(self, index: int | None = None) -> float: return 30.401
    def last_sector2(self, index: int | None = None) -> float: return 60.991
    def best_sector1(self, index: int | None = None) -> float: return 30.102
    def best_sector2(self, index: int | None = None) -> float: return 60.488
    def gap_to_leader(self, index: int | None = None) -> float: return 1.834


class _MockTyre(Tyre):
    def __init__(self, track_temp: Signal) -> None: self._track_temp = track_temp
    def compound(self, index: int | None = None) -> tuple[int, int]: return (0, 0)
    def compound_name(self, index: int | None = None) -> tuple[str, str]: return ("Dry", "Dry")
    def surface_temperature(self, index: int | None = None) -> tuple[float, ...]:
        base = self._track_temp.value + 18.0
        return (base, base + 1.2, base - 0.8, base + 0.6)
    def inner_temperature(self, index: int | None = None) -> tuple[float, ...]:
        base = self._track_temp.value + 11.0
        return (base, base + 0.8, base - 0.6, base + 0.4)
    def pressure(self, index: int | None = None) -> tuple[float, ...]: return (176.2, 176.8, 174.9, 175.3)
    def wear(self, index: int | None = None) -> tuple[float, ...]: return (0.97, 0.97, 0.98, 0.98)
    def load(self, index: int | None = None) -> tuple[float, ...]: return (3100.0, 3180.0, 2975.0, 3010.0)


class _MockVehicle(Vehicle):
    def __init__(self, fuel: Signal, speed: Signal) -> None:
        self._fuel = fuel
        self._speed = speed
    def player_index(self) -> int: return 0
    def is_player(self, index: int = 0) -> bool: return index == 0
    def total_vehicles(self) -> int: return 24
    def driver_name(self, index: int | None = None) -> str: return "Demo Driver"
    def vehicle_name(self, index: int | None = None) -> str: return "Mock GT3"
    def class_name(self, index: int | None = None) -> str: return "GT3"
    def place(self, index: int | None = None) -> int: return 3
    def in_pits(self, index: int | None = None) -> bool: return self._speed.value < 5.0
    def fuel(self, index: int | None = None) -> float: return self._fuel.value
    def speed(self, index: int | None = None) -> float: return self._speed.value / 3.6
    def position_xyz(self, index: int | None = None) -> tuple[float, float, float]: return (128.4, 0.2, 341.8)


class _MockOpponents(Opponents):
    def __init__(self, vehicle: _MockVehicle, lap: _MockLap, timing: _MockTiming) -> None:
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


class _MockWheel(Wheel):
    def camber(self, index: int | None = None) -> tuple[float, ...]: return (-0.041, -0.039, -0.028, -0.027)
    def rotation(self, index: int | None = None) -> tuple[float, ...]: return (83.0, 83.5, 80.7, 81.2)
    def ride_height(self, index: int | None = None) -> tuple[float, ...]: return (52.0, 52.0, 68.0, 68.0)
    def suspension_deflection(self, index: int | None = None) -> tuple[float, ...]: return (14.0, 13.5, 18.2, 18.0)


class MockTelemetryReader(TelemetryReader):
    """Shared fake telemetry reader used by the new connector family."""

    def __init__(self) -> None:
        self._fuel = Signal(minimum=0.5, maximum=105.0, step=0.35, value=92.0)
        self._speed = Signal(minimum=0.0, maximum=312.0, step=6.5, value=142.0)
        self._remaining = Signal(minimum=0.0, maximum=5400.0, step=1.0, value=4200.0)
        self._track_temp = Signal(minimum=18.0, maximum=38.0, step=0.15, value=27.5)
        self._ambient = Signal(minimum=12.0, maximum=26.0, step=0.08, value=19.0)
        self._opened = False
        self._state = _MockState()
        self._brake = _MockBrake(self._fuel)
        self._electric_motor = _MockElectricMotor()
        self._engine = _MockEngine(self._speed)
        self._inputs = _MockInputs(self._speed)
        self._lap = _MockLap(self._speed)
        self._session = _MockSession(self._remaining, self._track_temp, self._ambient)
        self._switch = _MockSwitch()
        self._timing = _MockTiming(self._speed)
        self._tyre = _MockTyre(self._track_temp)
        self._vehicle = _MockVehicle(self._fuel, self._speed)
        self._wheel = _MockWheel()
        self._track = _MockTrack(self._lap, self._session)
        self._opponents = _MockOpponents(self._vehicle, self._lap, self._timing)

    @property
    def min_val(self) -> float: return self._fuel.minimum
    @property
    def max_val(self) -> float: return self._fuel.maximum
    @property
    def step(self) -> float: return self._fuel.step

    def configure(self, minimum: float, maximum: float, step: float) -> None:
        if maximum <= minimum:
            maximum = minimum + 1.0
        safe_step = max(0.1, step)
        self._fuel.minimum = minimum
        self._fuel.maximum = maximum
        self._fuel.step = safe_step
        self._fuel.value = min(max(self._fuel.value, minimum), maximum)
        speed_min = max(0.0, minimum)
        speed_max = max(speed_min + 10.0, maximum * 3.0)
        self._speed.minimum = speed_min
        self._speed.maximum = speed_max
        self._speed.step = max(0.5, safe_step * 12.0)
        self._speed.value = min(max(self._speed.value, speed_min), speed_max)
        self._track_temp.minimum = 18.0
        self._track_temp.maximum = max(24.0, 18.0 + maximum / 5.0)
        self._track_temp.step = max(0.05, safe_step / 4.0)
        self._track_temp.value = min(max(self._track_temp.value, self._track_temp.minimum), self._track_temp.maximum)
        self._ambient.minimum = 12.0
        self._ambient.maximum = max(16.0, 12.0 + maximum / 8.0)
        self._ambient.step = max(0.03, safe_step / 6.0)
        self._ambient.value = min(max(self._ambient.value, self._ambient.minimum), self._ambient.maximum)

    def open(self) -> None: self._opened = True
    def close(self) -> None: self._opened = False
    def update(self) -> None:
        if not self._opened:
            return
        self._fuel.descend_wrap()
        self._speed.ping_pong()
        self._remaining.descend_wrap()
        self._track_temp.ping_pong()
        self._ambient.ping_pong()

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
    def switch(self) -> Switch: return self._switch
    @property
    def track(self) -> Track: return self._track
    @property
    def opponents(self) -> Opponents: return self._opponents
    @property
    def timing(self) -> Timing: return self._timing
    @property
    def tyre(self) -> Tyre: return self._tyre
    @property
    def vehicle(self) -> Vehicle: return self._vehicle
    @property
    def wheel(self) -> Wheel: return self._wheel
