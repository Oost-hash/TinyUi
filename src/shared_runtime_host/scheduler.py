"""Shared Qt clock driver for the runtime V2 scheduler."""

from __future__ import annotations

import time

from PySide6.QtCore import Qt, QTimer

from runtimeV2.capabilities.runtime_shutdown import RuntimeShutdown
from runtimeV2.events.contracts import EventType
from runtimeV2.events.startup_shutdown.startup import EventsStartupResult
from runtimeV2.runtime import RuntimeV2
from runtimeV2.scheduler.capabilities.scheduler_read import SchedulerRead
from runtimeV2.scheduler.capabilities.scheduler_write import SchedulerWrite


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

    def _on_runtime_shutdown(self, _event) -> None:
        self.stop()

    def _retime(self) -> None:
        interval_ms = self._runtime.capability("scheduler_read", SchedulerRead).minimum_interval_ms()
        self._timer.setInterval(max(5, interval_ms or 20))


def start_runtime_scheduler_clock(app, runtime: RuntimeV2) -> QmlRuntimeSchedulerDriver:
    """Start the shared Qt clock that drives runtime scheduler ticks."""

    driver = QmlRuntimeSchedulerDriver(runtime)
    driver.attach(app)
    app.setProperty("_runtimeSchedulerDriver", driver)
    return driver


def _monotonic_ms() -> int:
    return time.monotonic_ns() // 1_000_000
