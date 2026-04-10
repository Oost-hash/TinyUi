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

"""Read capability for runtime V2 scheduler jobs."""

from __future__ import annotations

from runtimeV2.contracts import ScheduledJobRecord
from runtimeV2.scheduler.registry import SchedulerRegistry


class SchedulerRead:
    """Read scheduler jobs and cadence metadata."""

    def __init__(self, registry: SchedulerRegistry) -> None:
        self._registry = registry

    def jobs(self) -> list[ScheduledJobRecord]:
        """Return all registered jobs."""

        return self._registry.jobs()

    def job(self, job_id: str) -> ScheduledJobRecord | None:
        """Return one registered job."""

        return self._registry.job(job_id)

    def minimum_interval_ms(self) -> int | None:
        """Return the smallest enabled job interval."""

        return self._registry.minimum_interval_ms()
