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

"""Startup for runtime V2 scheduler."""

from __future__ import annotations

from dataclasses import dataclass

from runtimeV2.events.startup_shutdown.startup import EventsStartupResult
from runtimeV2.runtime import RuntimeV2
from runtimeV2.scheduler.clock import SchedulerClock
from runtimeV2.scheduler.driver import SchedulerDriver
from runtimeV2.scheduler.registry import SchedulerRegistry
from runtimeV2.scheduler.startup_shutdown.register_capabilities import (
    SchedulerCapabilities,
    register_scheduler_capabilities,
)
from runtimeV2.scheduler.startup_shutdown.register_events import register_scheduler_events
from runtimeV2.schemas.startup import StartupResult, startup_error, startup_ok


@dataclass(frozen=True)
class SchedulerStartupResult:
    """Result of scheduler domain startup."""

    registry: SchedulerRegistry
    driver: SchedulerDriver
    clock: SchedulerClock
    capabilities: SchedulerCapabilities


def startup_scheduler(runtime: RuntimeV2) -> StartupResult:
    """Start runtime V2 scheduler."""

    try:
        events = runtime.domain_result("events", EventsStartupResult)
        register_scheduler_events(events.registry)
        registry = SchedulerRegistry()
        driver = SchedulerDriver(registry, events.bus)
        clock = SchedulerClock()
        capabilities = register_scheduler_capabilities(registry, driver, clock, events.bus)
        runtime.register_capability("scheduler_read", capabilities.read)
        runtime.register_capability("scheduler_write", capabilities.write)
        runtime.register_capability("scheduler_clock_read", capabilities.clock_read)
        runtime.register_capability("scheduler_clock_write", capabilities.clock_write)
        runtime.register_stop_hook("scheduler", capabilities.write.stop)
        runtime.register_domain_result(
            "scheduler",
            SchedulerStartupResult(
                registry=registry,
                driver=driver,
                clock=clock,
                capabilities=capabilities,
            ),
        )
        return startup_ok()
    except Exception as exc:
        return startup_error(f"Scheduler domain startup failed: {exc}")
