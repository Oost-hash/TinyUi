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

"""Runtime unit models for the core-owned runtime graph."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from .scheduling import RuntimeClock, RuntimeScheduleKind

RuntimeUnitKind = Literal["process", "worker", "timer", "adapter", "surface"]
RuntimeTransport = Literal["host", "qt_timer", "thread", "subprocess"]
RuntimeState = Literal[
    "declared",
    "starting",
    "running",
    "idle",
    "stopping",
    "stopped",
    "completed",
    "incomplete",
    "failed",
]
RuntimeExecutionPolicy = Literal["host", "subprocess", "thread"]
RuntimeActivationPolicy = Literal["boot", "always", "warm", "on_demand"]
RuntimeUpdateStage = Literal["refresh", "derive"]


@dataclass(frozen=True)
class RuntimeUnitSpec:
    """Declared metadata for one runtime-owned unit."""

    id: str
    kind: RuntimeUnitKind
    role: str
    owner: str
    transport: RuntimeTransport
    parent_id: str | None = None
    pid: int | None = None
    execution_policy: RuntimeExecutionPolicy = "host"
    activation_policy: RuntimeActivationPolicy = "always"
    start_order: int = 100
    stop_order: int = 100
    depends_on: tuple[str, ...] = ()
    schedule_kind: RuntimeScheduleKind = "manual"
    schedule_clock: RuntimeClock = "host"
    schedule_driver: str | None = None
    schedule_stage: RuntimeUpdateStage | None = None
    interval_ms: int | None = None
    delay_ms: int | None = None


@dataclass(frozen=True)
class RuntimeUnitInfo:
    """Runtime unit plus current lifecycle state."""

    id: str
    kind: RuntimeUnitKind
    role: str
    owner: str
    transport: RuntimeTransport
    state: RuntimeState
    parent_id: str | None = None
    pid: int | None = None
    execution_policy: RuntimeExecutionPolicy = "host"
    activation_policy: RuntimeActivationPolicy = "always"
    start_order: int = 100
    stop_order: int = 100
    depends_on: tuple[str, ...] = ()
    schedule_kind: RuntimeScheduleKind = "manual"
    schedule_clock: RuntimeClock = "host"
    schedule_driver: str | None = None
    schedule_stage: RuntimeUpdateStage | None = None
    interval_ms: int | None = None
    delay_ms: int | None = None
