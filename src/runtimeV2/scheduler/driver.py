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

"""Tick driver for runtime V2 scheduler jobs."""

from __future__ import annotations

from runtimeV2.contracts import EventBus, EventType, SchedulerTickData
from runtimeV2.scheduler.registry import SchedulerRegistry


class SchedulerDriver:
    """Run due scheduler jobs on incoming ticks."""

    def __init__(self, registry: SchedulerRegistry, events: EventBus | None = None) -> None:
        self._registry = registry
        self._events = events
        self._running = True

    def stop(self) -> None:
        """Stop processing future ticks."""

        self._running = False

    def tick(self, now_ms: int) -> list[str]:
        """Run due jobs for the current scheduler tick."""

        if not self._running:
            return []

        ran_jobs: list[str] = []
        for job in self._registry.due_jobs(now_ms):
            job.callback()
            job.last_tick_ms = now_ms
            ran_jobs.append(job.job_id)

        if self._events is not None:
            self._events.emit_typed(
                EventType.SCHEDULER_TICK,
                SchedulerTickData(now_ms=now_ms, ran_jobs=ran_jobs),
                source="scheduler",
            )
        return ran_jobs
