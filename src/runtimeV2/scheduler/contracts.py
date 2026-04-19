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

"""Contracts for runtime V2 scheduled work."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum

type SchedulerJobCallback = Callable[[], object | None]


class SchedulerClockMode(StrEnum):
    """Scheduler-owned central clock modes."""

    IDLE = "idle"
    NORMAL = "normal"
    LIVE = "live"


SCHEDULER_CLOCK_INTERVALS_MS: dict[SchedulerClockMode, int] = {
    SchedulerClockMode.IDLE: 5000,
    SchedulerClockMode.NORMAL: 1000,
    SchedulerClockMode.LIVE: 20,
}


@dataclass(frozen=True)
class ScheduledJobRecord:
    """Observable metadata for one scheduled runtime job."""

    job_id: str
    owner_domain: str
    interval_ms: int
    enabled: bool
    last_tick_ms: int | None = None


@dataclass(frozen=True)
class SchedulerJobRegisteredData:
    """Event payload for scheduler job registration."""

    job_id: str
    owner_domain: str
    interval_ms: int
    enabled: bool


@dataclass(frozen=True)
class SchedulerJobUpdatedData:
    """Event payload for scheduler job updates."""

    job_id: str
    owner_domain: str
    interval_ms: int
    enabled: bool


@dataclass(frozen=True)
class SchedulerTickData:
    """Event payload for one scheduler tick."""

    now_ms: int
    ran_jobs: list[str]


@dataclass(frozen=True)
class SchedulerClockState:
    """Observable state for the scheduler-owned central clock."""

    mode: SchedulerClockMode
    interval_ms: int
    locked_by: str | None = None
    running: bool = True


@dataclass(frozen=True)
class SchedulerClockUpdatedData:
    """Event payload for central scheduler clock state changes."""

    mode: str
    interval_ms: int
    locked_by: str | None
    running: bool
