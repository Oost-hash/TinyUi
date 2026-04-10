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

"""Write capability for the runtime V2 central scheduler clock."""

from __future__ import annotations

from runtimeV2.events.contracts import EventBus, EventType
from runtimeV2.scheduler.clock import SchedulerClock
from runtimeV2.scheduler.contracts import SchedulerClockUpdatedData


class SchedulerClockWrite:
    """Control the scheduler-owned central clock."""

    def __init__(
        self,
        clock: SchedulerClock,
        events: EventBus | None = None,
    ) -> None:
        self._clock = clock
        self._events = events

    def request_clock_mode(self, owner_domain: str, mode: str, *, lock: bool = False) -> bool:
        """Request a clock mode, optionally locking it for the owner."""

        previous = self._clock.state()
        try:
            accepted = self._clock.request_mode(owner_domain, mode, lock=lock)
        except ValueError:
            return False
        if accepted:
            self._emit_if_changed(previous)
        return accepted

    def release_clock_lock(self, owner_domain: str) -> bool:
        """Release the central clock lock for one owner."""

        previous = self._clock.state()
        accepted = self._clock.release_lock(owner_domain)
        if accepted:
            self._emit_if_changed(previous)
        return accepted

    def _emit_if_changed(self, previous) -> None:
        current = self._clock.state()
        if current == previous or self._events is None:
            return
        self._events.emit_typed(
            EventType.SCHEDULER_CLOCK_UPDATED,
            SchedulerClockUpdatedData(
                mode=current.mode.value,
                interval_ms=current.interval_ms,
                locked_by=current.locked_by,
                running=current.running,
            ),
            source="scheduler",
        )
