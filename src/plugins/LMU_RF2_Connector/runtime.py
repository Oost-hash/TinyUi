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

"""Runtime entrypoint and source orchestration for the consolidated connector family."""

from __future__ import annotations

from numbers import Real
from typing import Protocol, cast

from tinycore.inspect import InspectionSnapshot
from .contracts.source import ConnectorSource
from .contracts.telemetry import TelemetryReader
from .sources.lmu import LMULiveSource
from .sources.mock import MockSource
from .sources.rf2 import RF2LiveSource


class ConfigurableMockSource(Protocol):
    @property
    def min_val(self) -> float: ...

    @property
    def max_val(self) -> float: ...

    @property
    def step(self) -> float: ...

    def configure(self, minimum: float, maximum: float, step: float) -> None: ...


def _render_bool(value: object) -> str:
    return str(bool(value))


def _to_int(value: object) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        return int(value)
    raise TypeError(f"cannot render int from {type(value).__name__}")


def _to_float(value: object) -> float:
    if isinstance(value, bool):
        return float(value)
    if isinstance(value, Real):
        return float(value)
    if isinstance(value, str):
        return float(value)
    raise TypeError(f"cannot render float from {type(value).__name__}")


def _render_int(value: object) -> str:
    return str(_to_int(value))


def _render_float(value: object, digits: int = 2) -> str:
    return f"{_to_float(value):.{digits}f}"


def _render_kmh(value: object) -> str:
    return f"{_to_float(value) * 3.6:.1f} km/h"


def _render_seconds(value: object, digits: int = 1) -> str:
    return f"{_to_float(value):.{digits}f} s"


def _render_celsius(value: object) -> str:
    return f"{_to_float(value):.1f} C"


def _render_percent(value: object) -> str:
    return f"{_to_float(value) * 100:.1f} %"


def _render_join(values: object) -> str:
    if isinstance(values, tuple | list):
        return ", ".join(str(item) for item in values)
    return str(values)


class ConnectorRuntime(TelemetryReader):
    """Host-facing connector runtime that owns source selection and telemetry exposure."""

    family_name = "LMU_RF2_Connector"

    def __init__(self, *sources: ConnectorSource) -> None:
        self._sources: dict[str, ConnectorSource] = {}
        self._active_source_name: str | None = None
        self._opened = False
        self._demo_owners: set[str] = set()
        self._source_requests: dict[str, str] = {}
        self._preferred_source_name: str | None = None
        self.register_source(MockSource())
        for source in sources:
            self.register_source(source)
        if sources:
            self._active_source_name = sources[0].name

    def register_source(self, source: ConnectorSource) -> None:
        self._sources[source.name] = source
        if self._active_source_name is None:
            self._active_source_name = source.name
        if self._preferred_source_name is None and source.kind != "mock":
            self._preferred_source_name = source.name

    def source_names(self) -> tuple[str, ...]:
        return tuple(self._sources.keys())

    def source(self, name: str) -> ConnectorSource | None:
        return self._sources.get(name)

    def active_source_name(self) -> str | None:
        return self._active_source_name

    def active_source_handle(self) -> ConnectorSource | None:
        if self._active_source_name is None:
            return None
        return self._sources.get(self._active_source_name)

    def open(self) -> None:
        self._opened = True
        self._require_active_source().open()

    def close(self) -> None:
        active = self.active_source_handle()
        if active is not None:
            active.close()
        self._opened = False

    def update(self) -> None:
        self._require_active_source().update()

    def request_demo_mode(self, owner: str) -> None:
        self._demo_owners.add(owner)
        self._sync_active_source()

    def release_demo_mode(self, owner: str) -> None:
        self._demo_owners.discard(owner)
        self._sync_active_source()

    def supports_source(self, name: str) -> bool:
        return name in self._sources

    def request_source(self, owner: str, name: str) -> bool:
        if not self.supports_source(name):
            return False
        self._source_requests[owner] = name
        if name != "mock":
            self._preferred_source_name = name
        self._sync_active_source()
        return True

    def release_source(self, owner: str) -> bool:
        removed = self._source_requests.pop(owner, None)
        if removed is None:
            return False
        self._sync_active_source()
        return True

    def mode(self) -> str:
        active = self.active_source_handle()
        if active is None:
            return "inactive"
        return "demo" if active.kind == "mock" else "real"

    def active_game(self) -> str:
        active = self.active_source_handle()
        return active.game if active is not None else "none"

    def active_source(self) -> str:
        active = self.active_source_handle()
        return active.name if active is not None else "none"

    def supports_demo_mode(self) -> bool:
        return "mock" in self._sources

    def demo_owner_count(self) -> int:
        return len(self._demo_owners)

    def source_request_count(self) -> int:
        return len(self._source_requests)

    def demo_min(self) -> float:
        return self._mock_source().min_val if self.supports_demo_mode() else 0.0

    def demo_max(self) -> float:
        return self._mock_source().max_val if self.supports_demo_mode() else 0.0

    def demo_speed(self) -> float:
        return self._mock_source().step if self.supports_demo_mode() else 0.0

    def set_demo_min(self, value: float) -> None:
        mock = self._mock_source()
        mock.configure(value, mock.max_val, mock.step)

    def set_demo_max(self, value: float) -> None:
        mock = self._mock_source()
        mock.configure(mock.min_val, value, mock.step)

    def set_demo_speed(self, value: float) -> None:
        mock = self._mock_source()
        mock.configure(mock.min_val, mock.max_val, value)

    def inspect_snapshot(self) -> InspectionSnapshot:
        return [
            ("provider.family", self.family_name),
            ("provider.mode", self.mode()),
            ("provider.active_game", self.active_game()),
            ("provider.active_source", self.active_source()),
            ("provider.available_sources", _render_join(self.source_names())),
            ("provider.supports_demo", _render_bool(self.supports_demo_mode())),
            ("provider.demo_owner_count", _render_int(self.demo_owner_count())),
            ("provider.source_request_count", _render_int(self.source_request_count())),
            ("provider.demo_min", _render_float(self.demo_min())),
            ("provider.demo_max", _render_float(self.demo_max())),
            ("provider.demo_speed", _render_float(self.demo_speed())),
            ("state.active", _render_bool(self.state.active())),
            ("state.paused", _render_bool(self.state.paused())),
            ("state.version", str(self.state.version())),
            ("session.track", str(self.session.track_name())),
            ("session.kind", _render_int(self.session.session_kind())),
            ("session.is_race", _render_bool(self.session.is_race_session())),
            ("session.time_elapsed", _render_seconds(self.session.session_time_elapsed())),
            ("session.time_left", _render_seconds(self.session.session_time_left())),
            ("session.t_track", _render_celsius(self.session.track_temperature())),
            ("session.t_amb", _render_celsius(self.session.ambient_temperature())),
            ("session.raininess", _render_float(self.session.raininess())),
            ("track.name", str(self.track.name())),
            ("track.length", _render_float(self.track.length(), 1)),
            ("track.temperature", _render_celsius(self.track.temperature())),
            ("track.ambient_temperature", _render_celsius(self.track.ambient_temperature())),
            ("track.raininess", _render_float(self.track.raininess())),
            ("vehicle.player_idx", _render_int(self.vehicle.player_index())),
            ("vehicle.total", _render_int(self.vehicle.total_vehicles())),
            ("vehicle.driver", str(self.vehicle.driver_name())),
            ("vehicle.car", str(self.vehicle.vehicle_name())),
            ("vehicle.class", str(self.vehicle.class_name())),
            ("vehicle.place", _render_int(self.vehicle.place())),
            ("vehicle.in_pits", _render_bool(self.vehicle.in_pits())),
            ("vehicle.fuel", _render_float(self.vehicle.fuel())),
            ("vehicle.speed", _render_kmh(self.vehicle.speed())),
            ("opponents.total", _render_int(self.opponents.total())),
            ("opponents.p1.driver", str(self.opponents.driver_name(0))),
            ("opponents.p1.place", _render_int(self.opponents.place(0))),
            ("opponents.p1.in_pits", _render_bool(self.opponents.in_pits(0))),
            ("opponents.p1.gap_to_leader", _render_seconds(self.opponents.gap_to_leader(0), 3)),
            ("lap.current", _render_int(self.lap.current_lap())),
            ("lap.completed", _render_int(self.lap.completed_laps())),
            ("lap.distance", _render_float(self.lap.lap_distance(), 1)),
            ("lap.track_length", _render_float(self.lap.track_length(), 1)),
            ("lap.progress", _render_percent(self.lap.lap_progress())),
            ("lap.current_sector", _render_int(self.lap.current_sector())),
            ("engine.gear", _render_int(self.engine.gear())),
            ("engine.gear_max", _render_int(self.engine.gear_max())),
            ("engine.rpm", _render_int(self.engine.rpm())),
            ("engine.rpm_max", _render_int(self.engine.rpm_max())),
            ("engine.torque", _render_float(self.engine.torque())),
            ("engine.temp_oil", _render_celsius(self.engine.oil_temperature())),
            ("engine.temp_water", _render_celsius(self.engine.water_temperature())),
            ("emotor.state", _render_int(self.electric_motor.state())),
            ("emotor.battery", _render_float(self.electric_motor.battery_charge())),
            ("inputs.throttle", _render_float(self.inputs.throttle(), 3)),
            ("inputs.brake", _render_float(self.inputs.brake(), 3)),
            ("inputs.clutch", _render_float(self.inputs.clutch(), 3)),
            ("inputs.steering", _render_float(self.inputs.steering(), 3)),
            ("inputs.ffb", _render_float(self.inputs.force_feedback(), 3)),
            ("brake.bias_front", _render_float(self.brake.bias_front(), 3)),
            ("tyre.compound_f", str(self.tyre.compound_name()[0])),
            ("tyre.compound_r", str(self.tyre.compound_name()[1])),
            ("switch.headlights", _render_int(self.switch.headlights())),
            ("switch.speed_limiter", _render_int(self.switch.speed_limiter())),
            ("switch.drs", _render_int(self.switch.drs_status())),
            ("timing.current_lap", _render_seconds(self.timing.current_laptime(), 3)),
            ("timing.last_lap", _render_seconds(self.timing.last_laptime(), 3)),
            ("timing.best_lap", _render_seconds(self.timing.best_laptime(), 3)),
        ]

    @property
    def state(self):
        return self._reader.state

    @property
    def brake(self):
        return self._reader.brake

    @property
    def electric_motor(self):
        return self._reader.electric_motor

    @property
    def engine(self):
        return self._reader.engine

    @property
    def inputs(self):
        return self._reader.inputs

    @property
    def lap(self):
        return self._reader.lap

    @property
    def session(self):
        return self._reader.session

    @property
    def track(self):
        return self._reader.track

    @property
    def opponents(self):
        return self._reader.opponents

    @property
    def switch(self):
        return self._reader.switch

    @property
    def timing(self):
        return self._reader.timing

    @property
    def tyre(self):
        return self._reader.tyre

    @property
    def vehicle(self):
        return self._reader.vehicle

    @property
    def wheel(self):
        return self._reader.wheel

    @property
    def _reader(self) -> TelemetryReader:
        return self._require_active_source().reader

    def _switch_source(self, name: str) -> None:
        previous = self.active_source_handle()
        if previous is not None and previous.name == name:
            return
        was_open = self._opened
        if previous is not None and was_open:
            previous.close()
        self._active_source_name = name
        next_source = self._require_active_source()
        if next_source.kind != "mock":
            self._preferred_source_name = next_source.name
        if was_open:
            next_source.open()

    def _sync_active_source(self) -> None:
        target_name = self._requested_source_name()
        if target_name is not None:
            self._switch_source(target_name)

    def _require_active_source(self) -> ConnectorSource:
        active = self.active_source_handle()
        if active is None:
            raise RuntimeError("No active connector source has been registered")
        return active

    def _first_non_mock_source_name(self) -> str | None:
        for source in self._sources.values():
            if source.kind != "mock":
                return source.name
        return None

    def _requested_source_name(self) -> str | None:
        if self._demo_owners and self.supports_source("mock"):
            return "mock"
        if self._source_requests:
            return next(reversed(self._source_requests.values()))
        return self._preferred_source_name or self._first_non_mock_source_name()

    def _mock_source(self) -> ConfigurableMockSource:
        source = self.source("mock")
        if source is None:
            raise RuntimeError("Mock source is not registered")
        return cast(ConfigurableMockSource, source)


def create_provider(*sources: ConnectorSource) -> ConnectorRuntime:
    return ConnectorRuntime(*sources)


def create_lmu_provider() -> ConnectorRuntime:
    return create_provider(LMULiveSource())


def create_lmu_rf2_provider() -> ConnectorRuntime:
    return create_provider(LMULiveSource(), RF2LiveSource())
