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

"""Contracts for runtime V2 widgets."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class WidgetStatus(StrEnum):
    """Runtime V2 status for one widget record."""

    IDLE = "idle"
    WAITING_FOR_CONNECTOR = "waiting_for_connector"
    READY = "ready"
    HIDDEN = "hidden"
    ERROR = "error"


@dataclass(frozen=True)
class WidgetRecord:
    """Projected widget runtime record."""

    overlay_id: str
    widget_id: str
    widget_type: str
    label: str
    source: str
    bindings: dict[str, str]
    status: WidgetStatus
    connector_ids: tuple[str, ...]
    enabled: bool = True
    position: tuple[int, int] = (0, 0)
    values: dict[str, object] | None = None
    error_message: str = ""


@dataclass(frozen=True)
class WidgetVisibilityState:
    """Widget visibility read model."""

    global_visible: bool


@dataclass(frozen=True)
class WidgetRuntimeUpdatedData:
    """Data for widget runtime refresh events."""

    widget_count: int
