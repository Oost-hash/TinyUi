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

"""Write capability for runtime V2 scheduler jobs."""

from __future__ import annotations

from runtimeV2.events.contracts import EventBus, EventType
from runtimeV2.scheduler.contracts import (
    ScheduledJobRecord,
    SchedulerJobCallback,
    SchedulerJobRegisteredData,
    SchedulerJobUpdatedData,
)
from runtimeV2.scheduler.driver import SchedulerDriver
from runtimeV2.scheduler.registry import SchedulerRegistry


class SchedulerWrite:
    """Register and drive scheduled runtime jobs."""

    def __init__(
        self,
        registry: SchedulerRegistry,
        driver: SchedulerDriver,
        events: EventBus | None = None,
    ) -> None:
        self._registry = registry
        self._driver = driver
        self._events = events

    def register_job(
        self,
        *,
        job_id: str,
        owner_domain: str,
        interval_ms: int,
        callback: SchedulerJobCallback,
        enabled: bool = True,
    ) -> None:
        """Register one recurring runtime job."""

        existed = self._registry.job(job_id) is not None
        record = self._registry.register_job(
            job_id=job_id,
            owner_domain=owner_domain,
            interval_ms=interval_ms,
            callback=callback,
            enabled=enabled,
        )
        if self._events is None:
            return
        if existed:
            self._events.emit_typed(
                EventType.SCHEDULER_JOB_UPDATED,
                SchedulerJobUpdatedData(
                    job_id=record.job_id,
                    owner_domain=record.owner_domain,
                    interval_ms=record.interval_ms,
                    enabled=record.enabled,
                ),
                source="scheduler",
            )
            return
        self._events.emit_typed(
            EventType.SCHEDULER_JOB_REGISTERED,
            SchedulerJobRegisteredData(
                job_id=record.job_id,
                owner_domain=record.owner_domain,
                interval_ms=record.interval_ms,
                enabled=record.enabled,
            ),
            source="scheduler",
        )

    def set_enabled(self, job_id: str, enabled: bool) -> bool:
        """Enable or disable one registered job."""

        current = self._registry.job(job_id)
        if current is None:
            return False
        if current.enabled == enabled:
            return True
        record = self._registry.set_enabled(job_id, enabled)
        if record is None:
            return False
        self._emit_updated(record)
        return True

    def set_interval(self, job_id: str, interval_ms: int) -> bool:
        """Update one registered job interval."""

        current = self._registry.job(job_id)
        if current is None:
            return False
        safe_interval = max(1, int(interval_ms))
        if current.interval_ms == safe_interval:
            return True
        record = self._registry.set_interval(job_id, interval_ms)
        if record is None:
            return False
        self._emit_updated(record)
        return True

    def tick(self, now_ms: int) -> list[str]:
        """Run due jobs for the current scheduler tick."""

        return self._driver.tick(now_ms)

    def stop(self) -> None:
        """Stop the scheduler driver."""

        self._driver.stop()

    def _emit_updated(self, record: ScheduledJobRecord) -> None:
        if self._events is None:
            return
        self._events.emit_typed(
            EventType.SCHEDULER_JOB_UPDATED,
            SchedulerJobUpdatedData(
                job_id=record.job_id,
                owner_domain=record.owner_domain,
                interval_ms=record.interval_ms,
                enabled=record.enabled,
            ),
            source="scheduler",
        )
