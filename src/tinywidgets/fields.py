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
"""Host-side widget field contracts."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any


FieldGetter = Callable[[Any], object]


_FIELD_READERS: dict[str, dict[str, FieldGetter]] = {
    "telemetry.car.v1": {
        "fuel": lambda provider: provider.vehicle.fuel(),
        "speed": lambda provider: provider.vehicle.speed() * 3.6,
        "driver_name": lambda provider: provider.vehicle.driver_name(),
        "vehicle_name": lambda provider: provider.vehicle.vehicle_name(),
        "class_name": lambda provider: provider.vehicle.class_name(),
        "place": lambda provider: provider.vehicle.place(),
        "in_pits": lambda provider: provider.vehicle.in_pits(),
    },
    "telemetry.session.v1": {
        "track_name": lambda provider: provider.session.track_name(),
        "session_kind": lambda provider: provider.session.session_kind(),
        "session_time_elapsed": lambda provider: provider.session.session_time_elapsed(),
        "session_time_left": lambda provider: provider.session.session_time_left(),
        "track_temperature": lambda provider: provider.session.track_temperature(),
        "ambient_temperature": lambda provider: provider.session.ambient_temperature(),
        "raininess": lambda provider: provider.session.raininess(),
    },
}


def read_field(capability: str, field: str, provider: Any) -> object:
    """Read one widget field from a bound provider."""
    try:
        capability_fields = _FIELD_READERS[capability]
    except KeyError as exc:
        raise KeyError(f"No widget field contract registered for capability '{capability}'") from exc

    try:
        getter = capability_fields[field]
    except KeyError as exc:
        raise KeyError(
            f"Field '{field}' is not defined for capability '{capability}'"
        ) from exc

    return getter(provider)


def fields_for(capability: str) -> tuple[str, ...]:
    """Return the known widget field names for a capability."""
    return tuple(_FIELD_READERS.get(capability, {}))
