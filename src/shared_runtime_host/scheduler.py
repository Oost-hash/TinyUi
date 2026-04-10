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

"""Shared Qt clock driver for the runtime V2 scheduler."""

from __future__ import annotations

import time

from PySide6.QtCore import Qt, QTimer

from runtimeV2.capabilities.runtime_shutdown import RuntimeShutdown
from runtimeV2.events.contracts import EventType
from runtimeV2.events.startup_shutdown.startup import EventsStartupResult
from runtimeV2.runtime import RuntimeV2
from runtimeV2.scheduler.capabilities.scheduler_write import SchedulerWrite
from runtimeV2.scheduler.capabilities.scheduler_clock_read import SchedulerClockRead


class QmlRuntimeSchedulerDriver:
    """Drive runtime scheduler ticks from the Qt event loop."""

    def __init__(self, runtime: RuntimeV2) -> None:
        self._runtime = runtime
        self._timer = QTimer()
        self._timer.setTimerType(Qt.TimerType.PreciseTimer)
        self._timer.timeout.connect(self._on_timeout)

    def attach(self, app) -> None:
        """Attach the scheduler timer to the Qt application lifecycle."""

        self._timer.setParent(app)
        events = self._runtime.domain_result("events", EventsStartupResult)
        events.bus.on(EventType.RUNTIME_SHUTDOWN, self._on_runtime_shutdown)
        events.bus.on(EventType.SCHEDULER_JOB_REGISTERED, self._on_scheduler_jobs_changed)
        events.bus.on(EventType.SCHEDULER_JOB_UPDATED, self._on_scheduler_jobs_changed)
        events.bus.on(EventType.SCHEDULER_CLOCK_UPDATED, self._on_scheduler_jobs_changed)
        self._retime()
        self._timer.start()
        app.aboutToQuit.connect(self.stop)

    def stop(self) -> None:
        """Stop the shared scheduler clock."""

        self._timer.stop()

    def _on_timeout(self) -> None:
        shutdown = self._runtime.capability("shutdown", RuntimeShutdown)
        if shutdown.shutdown_requested():
            self.stop()
            return
        self._runtime.capability("scheduler_write", SchedulerWrite).tick(_monotonic_ms())
        self._retime()

    def _on_runtime_shutdown(self, _event) -> None:
        self.stop()

    def _on_scheduler_jobs_changed(self, _event) -> None:
        self._retime()

    def _retime(self) -> None:
        interval_ms = self._runtime.capability("scheduler_clock_read", SchedulerClockRead).clock_interval_ms()
        self._timer.setInterval(max(5, interval_ms))


def start_runtime_scheduler_clock(app, runtime: RuntimeV2) -> QmlRuntimeSchedulerDriver:
    """Start the shared Qt clock that drives runtime scheduler ticks."""

    driver = QmlRuntimeSchedulerDriver(runtime)
    driver.attach(app)
    app.setProperty("_runtimeSchedulerDriver", driver)
    return driver


def _monotonic_ms() -> int:
    return time.monotonic_ns() // 1_000_000
