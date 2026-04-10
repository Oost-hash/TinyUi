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

"""Public scheduler contracts used outside the scheduler domain."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from runtimeV2.scheduler.contracts import SchedulerClockState


@runtime_checkable
class SchedulerClockReader(Protocol):
    """Public contract for reading the central scheduler clock state."""

    def state(self) -> SchedulerClockState:
        """Return the current clock state."""
        ...

    def clock_mode(self) -> str:
        """Return the current clock mode."""
        ...

    def clock_interval_ms(self) -> int:
        """Return the current clock interval."""
        ...

    def clock_locked_by(self) -> str | None:
        """Return the current clock lock owner."""
        ...

    def clock_running(self) -> bool:
        """Return whether the central clock should run."""
        ...
