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
"""Mock connector — counts vehicle.fuel() from 100 down to 0, then loops.

Useful for testing threshold coloring and flash behaviour without a running game.
Decrements 0.5 per update() call (every 100 ms ≈ 20 s for a full sweep).
"""

from __future__ import annotations

from tinycore.telemetry.reader import (
    Brake, ElectricMotor, Engine, Inputs, Lap, Session, State, Switch,
    TelemetryReader, Timing, Tyre, Vehicle, WeatherNode, Wheel,
)


class _State(State):
    def active(self) -> bool:  return True
    def paused(self) -> bool:  return False
    def version(self) -> str:  return "mock"


class _Brake(Brake):
    def bias_front(self, index=None) -> float:          return 0.0
    def pressure(self, index=None, scale=1):            return (0.0, 0.0, 0.0, 0.0)
    def temperature(self, index=None):                  return (0.0, 0.0, 0.0, 0.0)
    def wear(self, index=None):                         return (0.0, 0.0, 0.0, 0.0)


class _ElectricMotor(ElectricMotor):
    def state(self, index=None) -> int:                 return 0
    def battery_charge(self, index=None) -> float:      return 0.0
    def rpm(self, index=None) -> float:                 return 0.0
    def torque(self, index=None) -> float:              return 0.0
    def motor_temperature(self, index=None) -> float:   return 0.0
    def water_temperature(self, index=None) -> float:   return 0.0


class _Engine(Engine):
    def gear(self, index=None) -> int:                  return 1
    def gear_max(self, index=None) -> int:              return 6
    def rpm(self, index=None) -> float:                 return 0.0
    def rpm_max(self, index=None) -> float:             return 8000.0
    def torque(self, index=None) -> float:              return 0.0
    def turbo(self, index=None) -> float:               return 0.0
    def oil_temperature(self, index=None) -> float:     return 0.0
    def water_temperature(self, index=None) -> float:   return 0.0


class _Inputs(Inputs):
    def throttle(self, index=None) -> float:            return 0.0
    def throttle_raw(self, index=None) -> float:        return 0.0
    def brake(self, index=None) -> float:               return 0.0
    def brake_raw(self, index=None) -> float:           return 0.0
    def clutch(self, index=None) -> float:              return 0.0
    def steering(self, index=None) -> float:            return 0.0
    def steering_raw(self, index=None) -> float:        return 0.0
    def force_feedback(self) -> float:                  return 0.0


class _Lap(Lap):
    def number(self, index=None) -> int:                return 1
    def completed_laps(self, index=None) -> int:        return 0
    def track_length(self) -> float:                    return 5000.0
    def distance(self, index=None) -> float:            return 0.0
    def progress(self, index=None) -> float:            return 0.0
    def sector_index(self, index=None) -> int:          return 0


class _Session(Session):
    def track_name(self) -> str:                        return "Mock Track"
    def elapsed(self) -> float:                         return 0.0
    def remaining(self) -> float:                       return 3600.0
    def session_type(self) -> int:                      return 4
    def in_race(self) -> bool:                          return True
    def track_temperature(self) -> float:               return 25.0
    def ambient_temperature(self) -> float:             return 20.0
    def raininess(self) -> float:                       return 0.0
    def weather_forecast(self):                         return ()


class _Switch(Switch):
    def headlights(self, index=None) -> int:            return 0
    def speed_limiter(self, index=None) -> int:         return 0
    def drs_status(self, index=None) -> int:            return 0


class _Timing(Timing):
    def current_laptime(self, index=None) -> float:     return 0.0
    def last_laptime(self, index=None) -> float:        return 0.0
    def best_laptime(self, index=None) -> float:        return 0.0
    def current_sector1(self, index=None) -> float:     return 0.0
    def current_sector2(self, index=None) -> float:     return 0.0
    def last_sector1(self, index=None) -> float:        return 0.0
    def last_sector2(self, index=None) -> float:        return 0.0
    def best_sector1(self, index=None) -> float:        return 0.0
    def best_sector2(self, index=None) -> float:        return 0.0
    def behind_leader(self, index=None) -> float:       return 0.0


class _Tyre(Tyre):
    def compound(self, index=None):                     return (0, 0)
    def compound_name(self, index=None):                return ("", "")
    def surface_temperature(self, index=None):          return (0.0, 0.0, 0.0, 0.0)
    def inner_temperature(self, index=None):            return (0.0, 0.0, 0.0, 0.0)
    def pressure(self, index=None):                     return (0.0, 0.0, 0.0, 0.0)
    def wear(self, index=None):                         return (0.0, 0.0, 0.0, 0.0)
    def load(self, index=None):                         return (0.0, 0.0, 0.0, 0.0)


class _Vehicle(Vehicle):

    def __init__(self, fuel_ref: list[float]) -> None:
        self._fuel = fuel_ref

    def player_index(self) -> int:                      return 0
    def is_player(self, index=0) -> bool:               return index == 0
    def total_vehicles(self) -> int:                    return 1
    def driver_name(self, index=None) -> str:           return "Mock Driver"
    def vehicle_name(self, index=None) -> str:          return "Mock Car"
    def class_name(self, index=None) -> str:            return "GT3"
    def place(self, index=None) -> int:                 return 1
    def in_pits(self, index=None) -> bool:              return False
    def fuel(self, index=None) -> float:                return self._fuel[0]
    def speed(self, index=None) -> float:               return 0.0
    def position_xyz(self, index=None):                 return (0.0, 0.0, 0.0)


class _Wheel(Wheel):
    def camber(self, index=None):                       return (0.0, 0.0, 0.0, 0.0)
    def rotation(self, index=None):                     return (0.0, 0.0, 0.0, 0.0)
    def ride_height(self, index=None):                  return (0.0, 0.0, 0.0, 0.0)
    def suspension_deflection(self, index=None):        return (0.0, 0.0, 0.0, 0.0)


# ---------------------------------------------------------------------------


class MockConnector(TelemetryReader):
    """Simulates a fuel value sweeping from max down to min, then looping.

    All parameters are live-editable via configure().
    """

    def __init__(
        self,
        min_val: float = 0.0,
        max_val: float = 100.0,
        step:    float = 0.5,
    ) -> None:
        self._min  = min_val
        self._max  = max_val
        self._step = step
        self._fuel: list[float] = [max_val]
        self._state          = _State()
        self._brake          = _Brake()
        self._electric_motor = _ElectricMotor()
        self._engine         = _Engine()
        self._inputs         = _Inputs()
        self._lap            = _Lap()
        self._session        = _Session()
        self._switch         = _Switch()
        self._timing         = _Timing()
        self._tyre           = _Tyre()
        self._vehicle        = _Vehicle(self._fuel)
        self._wheel          = _Wheel()

    # ── Configuration ─────────────────────────────────────────────────────────

    def configure(self, min_val: float, max_val: float, step: float) -> None:
        """Update sweep range and speed; resets the current value to max."""
        self._min  = min_val
        self._max  = max_val
        self._step = max(0.01, step)
        self._fuel[0] = self._max

    @property
    def min_val(self) -> float:  return self._min
    @property
    def max_val(self) -> float:  return self._max
    @property
    def step(self)    -> float:  return self._step

    # ── Connector lifecycle ───────────────────────────────────────────────────

    def open(self) -> None:
        self._fuel[0] = self._max

    def close(self) -> None:
        pass

    def update(self) -> None:
        self._fuel[0] -= self._step
        if self._fuel[0] < self._min:
            self._fuel[0] = self._max

    @property
    def state(self) -> State:           return self._state
    @property
    def brake(self) -> Brake:           return self._brake
    @property
    def electric_motor(self):           return self._electric_motor
    @property
    def engine(self) -> Engine:         return self._engine
    @property
    def inputs(self) -> Inputs:         return self._inputs
    @property
    def lap(self) -> Lap:               return self._lap
    @property
    def session(self) -> Session:       return self._session
    @property
    def switch(self) -> Switch:         return self._switch
    @property
    def timing(self) -> Timing:         return self._timing
    @property
    def tyre(self) -> Tyre:             return self._tyre
    @property
    def vehicle(self) -> Vehicle:       return self._vehicle
    @property
    def wheel(self) -> Wheel:           return self._wheel
