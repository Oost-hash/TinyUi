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

"""Read capability for the runtime V2 central scheduler clock."""

from __future__ import annotations

from runtimeV2.scheduler.clock import SchedulerClock
from runtimeV2.contracts import SchedulerClockState


class SchedulerClockRead:
    """Read the scheduler-owned central clock state."""

    def __init__(self, clock: SchedulerClock) -> None:
        self._clock = clock

    def state(self) -> SchedulerClockState:
        """Return the current clock state."""

        return self._clock.state()

    def clock_mode(self) -> str:
        """Return the current clock mode."""

        return self.state().mode.value

    def clock_interval_ms(self) -> int:
        """Return the current clock interval."""

        return self.state().interval_ms

    def clock_locked_by(self) -> str | None:
        """Return the current clock lock owner."""

        return self.state().locked_by

    def clock_running(self) -> bool:
        """Return whether the central clock should run."""

        return self.state().running
