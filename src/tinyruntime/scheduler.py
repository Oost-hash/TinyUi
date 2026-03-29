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

"""Core-owned delayed task scheduler for runtime units."""

from __future__ import annotations

from dataclasses import dataclass
import threading
from typing import Callable


@dataclass
class ScheduledTaskHandle:
    """Live handle for one scheduled delayed callback."""

    task_id: str
    timer: threading.Timer

    def cancel(self) -> None:
        self.timer.cancel()


class RuntimeScheduler:
    """Own delayed runtime callbacks such as warm shutdown grace timers."""

    def __init__(self) -> None:
        self._handles: dict[str, ScheduledTaskHandle] = {}
        self._lock = threading.Lock()

    def schedule_delay(
        self,
        task_id: str,
        *,
        delay_ms: int,
        callback: Callable[[], None],
    ) -> ScheduledTaskHandle:
        """Schedule or replace one delayed callback."""
        self.cancel(task_id)

        def _run() -> None:
            try:
                callback()
            finally:
                with self._lock:
                    self._handles.pop(task_id, None)

        timer = threading.Timer(delay_ms / 1000.0, _run)
        timer.daemon = True
        handle = ScheduledTaskHandle(task_id=task_id, timer=timer)
        with self._lock:
            self._handles[task_id] = handle
        timer.start()
        return handle

    def cancel(self, task_id: str) -> None:
        """Cancel one delayed callback if it is still pending."""
        with self._lock:
            handle = self._handles.pop(task_id, None)
        if handle is not None:
            handle.cancel()

    def shutdown(self) -> None:
        """Cancel all pending delayed callbacks."""
        with self._lock:
            handles = list(self._handles.values())
            self._handles.clear()
        for handle in handles:
            handle.cancel()

    def task_ids(self) -> tuple[str, ...]:
        """Return the currently scheduled task ids."""
        with self._lock:
            return tuple(sorted(self._handles))
