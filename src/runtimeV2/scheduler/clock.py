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

"""Central scheduler clock state for runtime V2."""

from __future__ import annotations

from runtimeV2.contracts import (
    SCHEDULER_CLOCK_INTERVALS_MS,
    SchedulerClockMode,
    SchedulerClockState,
)


class SchedulerClock:
    """Store central scheduler clock requests and lock state."""

    _MODE_PRIORITY: dict[SchedulerClockMode, int] = {
        SchedulerClockMode.IDLE: 0,
        SchedulerClockMode.NORMAL: 1,
        SchedulerClockMode.LIVE: 2,
    }

    def __init__(self) -> None:
        self._requests: dict[str, SchedulerClockMode] = {}
        self._locked_by: str | None = None

    def state(self) -> SchedulerClockState:
        """Return the current central clock state."""

        mode = self._active_mode()
        return SchedulerClockState(
            mode=mode,
            interval_ms=SCHEDULER_CLOCK_INTERVALS_MS[mode],
            locked_by=self._locked_by,
            running=True,
        )

    def request_mode(self, owner_domain: str, mode: str | SchedulerClockMode, *, lock: bool = False) -> bool:
        """Request a clock mode, optionally locking it for the owner."""

        owner = owner_domain.strip()
        if not owner:
            return False
        clock_mode = SchedulerClockMode(mode)
        if self._locked_by is not None and self._locked_by != owner:
            return False
        self._requests[owner] = clock_mode
        if lock:
            self._locked_by = owner
        return True

    def release_lock(self, owner_domain: str) -> bool:
        """Release the central clock lock for one owner."""

        owner = owner_domain.strip()
        if self._locked_by is None:
            return True
        if self._locked_by != owner:
            return False
        self._locked_by = None
        return True

    def _active_mode(self) -> SchedulerClockMode:
        if self._locked_by is not None:
            return self._requests.get(self._locked_by, SchedulerClockMode.IDLE)
        if not self._requests:
            return SchedulerClockMode.IDLE
        return max(self._requests.values(), key=lambda mode: self._MODE_PRIORITY[mode])
