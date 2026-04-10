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

"""Capability registration for runtime V2 scheduler."""

from __future__ import annotations

from dataclasses import dataclass

from runtimeV2.events.contracts import EventBus
from runtimeV2.scheduler.capabilities.scheduler_clock_read import SchedulerClockRead
from runtimeV2.scheduler.capabilities.scheduler_clock_write import SchedulerClockWrite
from runtimeV2.scheduler.capabilities.scheduler_read import SchedulerRead
from runtimeV2.scheduler.capabilities.scheduler_write import SchedulerWrite
from runtimeV2.scheduler.clock import SchedulerClock
from runtimeV2.scheduler.driver import SchedulerDriver
from runtimeV2.scheduler.registry import SchedulerRegistry


@dataclass(frozen=True)
class SchedulerCapabilities:
    """Capabilities exposed by the scheduler domain."""

    read: SchedulerRead
    write: SchedulerWrite
    clock_read: SchedulerClockRead
    clock_write: SchedulerClockWrite


def register_scheduler_capabilities(
    registry: SchedulerRegistry,
    driver: SchedulerDriver,
    clock: SchedulerClock,
    events: EventBus | None = None,
) -> SchedulerCapabilities:
    """Create scheduler domain capabilities."""

    return SchedulerCapabilities(
        read=SchedulerRead(registry),
        write=SchedulerWrite(registry, driver, events),
        clock_read=SchedulerClockRead(clock),
        clock_write=SchedulerClockWrite(clock, events),
    )
