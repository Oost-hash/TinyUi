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

"""Declarative inspection schema for the consolidated connector family."""

from __future__ import annotations

from tinycore.inspect.schema import InspectionFieldSchema, RenderKind


def _field(
    key: str,
    path: str,
    render: RenderKind = "auto",
    *,
    args: tuple[object, ...] = (),
    item: int | None = None,
) -> InspectionFieldSchema:
    return InspectionFieldSchema(key, path, render, args, item)


_PROVIDER_FIELDS = (
    _field("provider.family", "family_name", "str"),
    _field("provider.mode", "mode", "str"),
    _field("provider.active_game", "active_game", "str"),
    _field("provider.active_source", "active_source", "str"),
    _field("provider.available_sources", "source_names", "join"),
    _field("provider.supports_demo", "supports_demo_mode", "bool"),
    _field("provider.demo_owner_count", "demo_owner_count", "int"),
    _field("provider.source_request_count", "source_request_count", "int"),
    _field("provider.demo_min", "demo_min", "float_2"),
    _field("provider.demo_max", "demo_max", "float_2"),
    _field("provider.demo_speed", "demo_speed", "float_2"),
)

_STATE_FIELDS = (
    _field("state.active", "state.active", "bool"),
    _field("state.paused", "state.paused", "bool"),
    _field("state.version", "state.version", "str"),
)

_SESSION_FIELDS = (
    _field("session.track", "session.track_name", "str"),
    _field("session.kind", "session.session_kind", "int"),
    _field("session.is_race", "session.is_race_session", "bool"),
    _field("session.time_elapsed", "session.session_time_elapsed", "seconds_1"),
    _field("session.time_left", "session.session_time_left", "seconds_1"),
    _field("session.t_track", "session.track_temperature", "celsius_1"),
    _field("session.t_amb", "session.ambient_temperature", "celsius_1"),
    _field("session.raininess", "session.raininess", "float_2"),
)

_TRACK_FIELDS = (
    _field("track.name", "track.name", "str"),
    _field("track.length", "track.length", "float_1"),
    _field("track.temperature", "track.temperature", "celsius_1"),
    _field("track.ambient_temperature", "track.ambient_temperature", "celsius_1"),
    _field("track.raininess", "track.raininess", "float_2"),
)

_VEHICLE_FIELDS = (
    _field("vehicle.player_idx", "vehicle.player_index", "int"),
    _field("vehicle.total", "vehicle.total_vehicles", "int"),
    _field("vehicle.driver", "vehicle.driver_name", "str"),
    _field("vehicle.car", "vehicle.vehicle_name", "str"),
    _field("vehicle.class", "vehicle.class_name", "str"),
    _field("vehicle.place", "vehicle.place", "int"),
    _field("vehicle.in_pits", "vehicle.in_pits", "bool"),
    _field("vehicle.fuel", "vehicle.fuel", "float_2"),
    _field("vehicle.speed", "vehicle.speed", "kmh_1"),
)

_OPPONENT_FIELDS = (
    _field("opponents.total", "opponents.total", "int"),
    _field("opponents.p1.driver", "opponents.driver_name", "str", args=(0,)),
    _field("opponents.p1.place", "opponents.place", "int", args=(0,)),
    _field("opponents.p1.in_pits", "opponents.in_pits", "bool", args=(0,)),
    _field("opponents.p1.gap_to_leader", "opponents.gap_to_leader", "seconds_3", args=(0,)),
)

_LAP_FIELDS = (
    _field("lap.current", "lap.current_lap", "int"),
    _field("lap.completed", "lap.completed_laps", "int"),
    _field("lap.distance", "lap.lap_distance", "float_1"),
    _field("lap.track_length", "lap.track_length", "float_1"),
    _field("lap.progress", "lap.lap_progress", "percent_1"),
    _field("lap.current_sector", "lap.current_sector", "int"),
)

_ENGINE_FIELDS = (
    _field("engine.gear", "engine.gear", "int"),
    _field("engine.gear_max", "engine.gear_max", "int"),
    _field("engine.rpm", "engine.rpm", "int"),
    _field("engine.rpm_max", "engine.rpm_max", "int"),
    _field("engine.torque", "engine.torque", "float_2"),
    _field("engine.temp_oil", "engine.oil_temperature", "celsius_1"),
    _field("engine.temp_water", "engine.water_temperature", "celsius_1"),
)

_ELECTRIC_FIELDS = (
    _field("emotor.state", "electric_motor.state", "int"),
    _field("emotor.battery", "electric_motor.battery_charge", "float_2"),
)

_INPUT_FIELDS = (
    _field("inputs.throttle", "inputs.throttle", "float_3"),
    _field("inputs.brake", "inputs.brake", "float_3"),
    _field("inputs.clutch", "inputs.clutch", "float_3"),
    _field("inputs.steering", "inputs.steering", "float_3"),
    _field("inputs.ffb", "inputs.force_feedback", "float_3"),
)

_BRAKE_FIELDS = (
    _field("brake.bias_front", "brake.bias_front", "float_3"),
)

_TYRE_FIELDS = (
    _field("tyre.compound_f", "tyre.compound_name", "str", item=0),
    _field("tyre.compound_r", "tyre.compound_name", "str", item=1),
)

_SWITCH_FIELDS = (
    _field("switch.headlights", "switch.headlights", "int"),
    _field("switch.speed_limiter", "switch.speed_limiter", "int"),
    _field("switch.drs", "switch.drs_status", "int"),
)

_TIMING_FIELDS = (
    _field("timing.current_lap", "timing.current_laptime", "seconds_3"),
    _field("timing.last_lap", "timing.last_laptime", "seconds_3"),
    _field("timing.best_lap", "timing.best_laptime", "seconds_3"),
)


def provider_inspection_schema() -> tuple[InspectionFieldSchema, ...]:
    """Describe provider and telemetry fields for TinyUi-driven inspection."""

    return (
        *_PROVIDER_FIELDS,
        *_STATE_FIELDS,
        *_SESSION_FIELDS,
        *_TRACK_FIELDS,
        *_VEHICLE_FIELDS,
        *_OPPONENT_FIELDS,
        *_LAP_FIELDS,
        *_ENGINE_FIELDS,
        *_ELECTRIC_FIELDS,
        *_INPUT_FIELDS,
        *_BRAKE_FIELDS,
        *_TYRE_FIELDS,
        *_SWITCH_FIELDS,
        *_TIMING_FIELDS,
    )
