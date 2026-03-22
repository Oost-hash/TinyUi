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
"""Telemetry reader ABCs.

Defines the contract any game connector must implement.
Each class covers one domain of telemetry data. A concrete connector
implements TelemetryReader and exposes all sub-readers as properties.

Ported and adapted from TinyPedal's adapter/_reader.py.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class WeatherNode:
    """A single weather forecast entry."""
    time: float       # seconds from now
    raininess: float  # fraction 0–1
    temperature: float  # Celsius


# ---------------------------------------------------------------------------
# Sub-readers
# ---------------------------------------------------------------------------

class State(ABC):
    """Connection and session state."""

    __slots__ = ()

    @abstractmethod
    def active(self) -> bool:
        """Is active (driving or overriding)."""

    @abstractmethod
    def paused(self) -> bool:
        """Is paused."""

    @abstractmethod
    def version(self) -> str:
        """API / game version string."""


class Brake(ABC):
    """Brake data."""

    __slots__ = ()

    @abstractmethod
    def bias_front(self, index: int | None = None) -> float:
        """Brake bias front (fraction)."""

    @abstractmethod
    def pressure(self, index: int | None = None, scale: float = 1) -> tuple[float, ...]:
        """Brake pressure (fraction)."""

    @abstractmethod
    def temperature(self, index: int | None = None) -> tuple[float, ...]:
        """Brake temperature (Celsius)."""

    @abstractmethod
    def wear(self, index: int | None = None) -> tuple[float, ...]:
        """Brake remaining thickness (meters)."""


class ElectricMotor(ABC):
    """Electric motor / hybrid data."""

    __slots__ = ()

    @abstractmethod
    def state(self, index: int | None = None) -> int:
        """Motor state: 0=n/a, 1=off, 2=drain, 3=regen."""

    @abstractmethod
    def battery_charge(self, index: int | None = None) -> float:
        """Battery charge (fraction)."""

    @abstractmethod
    def rpm(self, index: int | None = None) -> float:
        """Motor RPM."""

    @abstractmethod
    def torque(self, index: int | None = None) -> float:
        """Motor torque (Nm)."""

    @abstractmethod
    def motor_temperature(self, index: int | None = None) -> float:
        """Motor temperature (Celsius)."""

    @abstractmethod
    def water_temperature(self, index: int | None = None) -> float:
        """Motor water temperature (Celsius)."""


class Engine(ABC):
    """Engine data."""

    __slots__ = ()

    @abstractmethod
    def gear(self, index: int | None = None) -> int:
        """Current gear."""

    @abstractmethod
    def gear_max(self, index: int | None = None) -> int:
        """Max gear."""

    @abstractmethod
    def rpm(self, index: int | None = None) -> float:
        """RPM."""

    @abstractmethod
    def rpm_max(self, index: int | None = None) -> float:
        """Max RPM."""

    @abstractmethod
    def torque(self, index: int | None = None) -> float:
        """Torque (Nm)."""

    @abstractmethod
    def turbo(self, index: int | None = None) -> float:
        """Turbo pressure (Pa)."""

    @abstractmethod
    def oil_temperature(self, index: int | None = None) -> float:
        """Oil temperature (Celsius)."""

    @abstractmethod
    def water_temperature(self, index: int | None = None) -> float:
        """Water temperature (Celsius)."""


class Inputs(ABC):
    """Driver input data."""

    __slots__ = ()

    @abstractmethod
    def throttle(self, index: int | None = None) -> float:
        """Throttle filtered (fraction)."""

    @abstractmethod
    def throttle_raw(self, index: int | None = None) -> float:
        """Throttle raw (fraction)."""

    @abstractmethod
    def brake(self, index: int | None = None) -> float:
        """Brake filtered (fraction)."""

    @abstractmethod
    def brake_raw(self, index: int | None = None) -> float:
        """Brake raw (fraction)."""

    @abstractmethod
    def clutch(self, index: int | None = None) -> float:
        """Clutch filtered (fraction)."""

    @abstractmethod
    def steering(self, index: int | None = None) -> float:
        """Steering filtered (fraction)."""

    @abstractmethod
    def steering_raw(self, index: int | None = None) -> float:
        """Steering raw (fraction)."""

    @abstractmethod
    def force_feedback(self) -> float:
        """Steering force feedback (fraction)."""


class Lap(ABC):
    """Lap data."""

    __slots__ = ()

    @abstractmethod
    def number(self, index: int | None = None) -> int:
        """Current lap number."""

    @abstractmethod
    def completed_laps(self, index: int | None = None) -> int:
        """Total completed laps."""

    @abstractmethod
    def track_length(self) -> float:
        """Full track length (meters)."""

    @abstractmethod
    def distance(self, index: int | None = None) -> float:
        """Distance into lap (meters)."""

    @abstractmethod
    def progress(self, index: int | None = None) -> float:
        """Lap progress (fraction)."""

    @abstractmethod
    def sector_index(self, index: int | None = None) -> int:
        """Sector index: 0=S1, 1=S2, 2=S3."""


class Session(ABC):
    """Session data."""

    __slots__ = ()

    @abstractmethod
    def track_name(self) -> str:
        """Track name."""

    @abstractmethod
    def elapsed(self) -> float:
        """Session elapsed time (seconds)."""

    @abstractmethod
    def remaining(self) -> float:
        """Session time remaining (seconds)."""

    @abstractmethod
    def session_type(self) -> int:
        """Session type: 0=test, 1=practice, 2=qualify, 3=warmup, 4=race."""

    @abstractmethod
    def in_race(self) -> bool:
        """Is in race session."""

    @abstractmethod
    def track_temperature(self) -> float:
        """Track temperature (Celsius)."""

    @abstractmethod
    def ambient_temperature(self) -> float:
        """Ambient temperature (Celsius)."""

    @abstractmethod
    def raininess(self) -> float:
        """Rain severity (fraction)."""

    @abstractmethod
    def weather_forecast(self) -> tuple[WeatherNode, ...]:
        """Weather forecast nodes."""


class Switch(ABC):
    """Vehicle switch states."""

    __slots__ = ()

    @abstractmethod
    def headlights(self, index: int | None = None) -> int:
        """Headlights state."""

    @abstractmethod
    def speed_limiter(self, index: int | None = None) -> int:
        """Speed limiter state."""

    @abstractmethod
    def drs_status(self, index: int | None = None) -> int:
        """DRS status: 0=unavailable, 1=available, 2=allowed, 3=activated."""


class Timing(ABC):
    """Lap timing data."""

    __slots__ = ()

    @abstractmethod
    def current_laptime(self, index: int | None = None) -> float:
        """Current lap time (seconds)."""

    @abstractmethod
    def last_laptime(self, index: int | None = None) -> float:
        """Last lap time (seconds)."""

    @abstractmethod
    def best_laptime(self, index: int | None = None) -> float:
        """Best lap time (seconds)."""

    @abstractmethod
    def current_sector1(self, index: int | None = None) -> float:
        """Current lap S1 time (seconds)."""

    @abstractmethod
    def current_sector2(self, index: int | None = None) -> float:
        """Current lap S1+S2 time (seconds)."""

    @abstractmethod
    def last_sector1(self, index: int | None = None) -> float:
        """Last lap S1 time (seconds)."""

    @abstractmethod
    def last_sector2(self, index: int | None = None) -> float:
        """Last lap S1+S2 time (seconds)."""

    @abstractmethod
    def best_sector1(self, index: int | None = None) -> float:
        """Best S1 time (seconds)."""

    @abstractmethod
    def best_sector2(self, index: int | None = None) -> float:
        """Best S1+S2 time (seconds)."""

    @abstractmethod
    def behind_leader(self, index: int | None = None) -> float:
        """Time behind leader (seconds)."""


class Tyre(ABC):
    """Tyre data."""

    __slots__ = ()

    @abstractmethod
    def compound(self, index: int | None = None) -> tuple[int, int]:
        """Tyre compound (front, rear)."""

    @abstractmethod
    def compound_name(self, index: int | None = None) -> tuple[str, str]:
        """Tyre compound name (front, rear)."""

    @abstractmethod
    def surface_temperature(self, index: int | None = None) -> tuple[float, ...]:
        """Tyre surface temperature set (Celsius)."""

    @abstractmethod
    def inner_temperature(self, index: int | None = None) -> tuple[float, ...]:
        """Tyre inner temperature set (Celsius)."""

    @abstractmethod
    def pressure(self, index: int | None = None) -> tuple[float, ...]:
        """Tyre pressure (kPa)."""

    @abstractmethod
    def wear(self, index: int | None = None) -> tuple[float, ...]:
        """Tyre wear (fraction)."""

    @abstractmethod
    def load(self, index: int | None = None) -> tuple[float, ...]:
        """Tyre load (Newtons)."""


class Vehicle(ABC):
    """Vehicle and standings data."""

    __slots__ = ()

    @abstractmethod
    def player_index(self) -> int:
        """Local player index."""

    @abstractmethod
    def is_player(self, index: int = 0) -> bool:
        """Is local player."""

    @abstractmethod
    def total_vehicles(self) -> int:
        """Total vehicles on track."""

    @abstractmethod
    def driver_name(self, index: int | None = None) -> str:
        """Driver name."""

    @abstractmethod
    def vehicle_name(self, index: int | None = None) -> str:
        """Vehicle name."""

    @abstractmethod
    def class_name(self, index: int | None = None) -> str:
        """Vehicle class name."""

    @abstractmethod
    def place(self, index: int | None = None) -> int:
        """Overall race position."""

    @abstractmethod
    def in_pits(self, index: int | None = None) -> bool:
        """Is in pit lane."""

    @abstractmethod
    def fuel(self, index: int | None = None) -> float:
        """Remaining fuel (liters)."""

    @abstractmethod
    def speed(self, index: int | None = None) -> float:
        """Speed (m/s)."""

    @abstractmethod
    def position_xyz(self, index: int | None = None) -> tuple[float, float, float]:
        """Raw x,y,z position (meters)."""


class Wheel(ABC):
    """Wheel and suspension data."""

    __slots__ = ()

    @abstractmethod
    def camber(self, index: int | None = None) -> tuple[float, ...]:
        """Wheel camber (radians)."""

    @abstractmethod
    def rotation(self, index: int | None = None) -> tuple[float, ...]:
        """Wheel rotation (radians per second)."""

    @abstractmethod
    def ride_height(self, index: int | None = None) -> tuple[float, ...]:
        """Ride height (millimeters)."""

    @abstractmethod
    def suspension_deflection(self, index: int | None = None) -> tuple[float, ...]:
        """Suspension deflection (millimeters)."""


# ---------------------------------------------------------------------------
# Top-level connector contract
# ---------------------------------------------------------------------------

class TelemetryReader(ABC):
    """Contract for a game connector.

    A connector opens the game's data source (shared memory, UDP, etc.),
    implements all sub-readers, and exposes them as properties.

    Usage in a plugin:
        reader = LMUConnector()
        reader.open()
        ctx.connector.register(reader)
    """

    @abstractmethod
    def open(self) -> None:
        """Open the data source."""

    @abstractmethod
    def close(self) -> None:
        """Close the data source."""

    @abstractmethod
    def update(self) -> None:
        """Copy latest frame from the data source."""

    # --- Sub-readers ---

    @property
    @abstractmethod
    def state(self) -> State: ...

    @property
    @abstractmethod
    def brake(self) -> Brake: ...

    @property
    @abstractmethod
    def electric_motor(self) -> ElectricMotor: ...

    @property
    @abstractmethod
    def engine(self) -> Engine: ...

    @property
    @abstractmethod
    def inputs(self) -> Inputs: ...

    @property
    @abstractmethod
    def lap(self) -> Lap: ...

    @property
    @abstractmethod
    def session(self) -> Session: ...

    @property
    @abstractmethod
    def switch(self) -> Switch: ...

    @property
    @abstractmethod
    def timing(self) -> Timing: ...

    @property
    @abstractmethod
    def tyre(self) -> Tyre: ...

    @property
    @abstractmethod
    def vehicle(self) -> Vehicle: ...

    @property
    @abstractmethod
    def wheel(self) -> Wheel: ...
