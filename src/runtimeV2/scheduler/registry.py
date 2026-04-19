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

"""Registry for runtime V2 scheduled jobs."""

from __future__ import annotations

from runtimeV2.scheduler.contracts import ScheduledJobRecord, SchedulerJobCallback


class SchedulerRegistry:
    """Store recurring runtime jobs and their cadence."""

    def __init__(self) -> None:
        self._jobs: dict[str, _ScheduledJob] = {}

    def register_job(
        self,
        *,
        job_id: str,
        owner_domain: str,
        interval_ms: int,
        callback: SchedulerJobCallback,
        enabled: bool = True,
    ) -> ScheduledJobRecord:
        """Register or replace one recurring job."""

        safe_interval = max(1, int(interval_ms))
        job = self._jobs.get(job_id)
        if job is None:
            job = _ScheduledJob(
                job_id=job_id,
                owner_domain=owner_domain,
                interval_ms=safe_interval,
                enabled=enabled,
                callback=callback,
            )
            self._jobs[job_id] = job
        else:
            job.owner_domain = owner_domain
            job.interval_ms = safe_interval
            job.enabled = enabled
            job.callback = callback
        return job.record()

    def jobs(self) -> list[ScheduledJobRecord]:
        """Return scheduler-visible job metadata."""

        return [job.record() for job in self._jobs.values()]

    def job(self, job_id: str) -> ScheduledJobRecord | None:
        """Return one scheduler-visible job metadata record."""

        entry = self._jobs.get(job_id)
        return None if entry is None else entry.record()

    def set_enabled(self, job_id: str, enabled: bool) -> ScheduledJobRecord | None:
        """Enable or disable one job."""

        entry = self._jobs.get(job_id)
        if entry is None:
            return None
        entry.enabled = enabled
        return entry.record()

    def set_interval(self, job_id: str, interval_ms: int) -> ScheduledJobRecord | None:
        """Update one job interval."""

        entry = self._jobs.get(job_id)
        if entry is None:
            return None
        entry.interval_ms = max(1, int(interval_ms))
        return entry.record()

    def minimum_interval_ms(self) -> int | None:
        """Return the smallest enabled job interval."""

        intervals = [job.interval_ms for job in self._jobs.values() if job.enabled]
        return min(intervals) if intervals else None

    def due_jobs(self, now_ms: int) -> list[_ScheduledJob]:
        """Return enabled jobs that should run at the current tick."""

        due: list[_ScheduledJob] = []
        for job in self._jobs.values():
            if not job.enabled:
                continue
            if job.last_tick_ms is None or now_ms - job.last_tick_ms >= job.interval_ms:
                due.append(job)
        return due


class _ScheduledJob:
    """Mutable scheduler-owned recurring job."""

    def __init__(
        self,
        *,
        job_id: str,
        owner_domain: str,
        interval_ms: int,
        enabled: bool,
        callback: SchedulerJobCallback,
    ) -> None:
        self.job_id = job_id
        self.owner_domain = owner_domain
        self.interval_ms = interval_ms
        self.enabled = enabled
        self.callback = callback
        self.last_tick_ms: int | None = None

    def record(self) -> ScheduledJobRecord:
        return ScheduledJobRecord(
            job_id=self.job_id,
            owner_domain=self.owner_domain,
            interval_ms=self.interval_ms,
            enabled=self.enabled,
            last_tick_ms=self.last_tick_ms,
        )
