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

"""Runtime-owned widget refresh policy."""

from __future__ import annotations

from runtimeV2.events.contracts import Event, EventBus, EventType
from runtimeV2.contracts import SchedulerClockReader, SchedulerWriter
from runtimeV2.widgets.capabilities.widget_records_refresh import WidgetRecordsRefresh
from runtimeV2.widgets.capabilities.widget_visibility_read import WidgetVisibilityRead


class WidgetRefreshPolicy:
    """Refresh widget runtime records from a scheduler-owned job."""

    JOB_ID = "widgets.project_records"
    JOB_INTERVAL_MS = 20

    _VISIBILITY_EVENTS = (
        EventType.WIDGET_VISIBILITY_CHANGED,
    )

    def __init__(
        self,
        *,
        records_refresh: WidgetRecordsRefresh,
        visibility_read: WidgetVisibilityRead,
        scheduler_write: SchedulerWriter,
        scheduler_clock_read: SchedulerClockReader,
        events: EventBus,
    ) -> None:
        self._records_refresh = records_refresh
        self._visibility_read = visibility_read
        self._scheduler_write = scheduler_write
        self._scheduler_clock_read = scheduler_clock_read
        self._events = events
        self._attached = False
        self._refreshing = False

    def attach(self) -> None:
        """Register widget refresh as scheduler job and subscribe to visibility updates."""

        if self._attached:
            return
        self._attached = True
        self._scheduler_write.register_job(
            job_id=self.JOB_ID,
            owner_domain="widgets",
            interval_ms=self.JOB_INTERVAL_MS,
            callback=self.refresh_if_live_and_visible,
            enabled=True,
        )
        for event_type in self._VISIBILITY_EVENTS:
            self._events.on(event_type, self._on_visibility_event)

    def close(self) -> None:
        """Detach the refresh policy from runtime triggers."""

        if not self._attached:
            return
        self._attached = False
        self._scheduler_write.set_enabled(self.JOB_ID, False)
        for event_type in self._VISIBILITY_EVENTS:
            self._events.off(event_type, self._on_visibility_event)

    def refresh_if_live_and_visible(self) -> bool:
        """Refresh widgets when the central clock is live and widgets are visible."""

        # Always refresh if widgets are visible, regardless of clock mode
        # This ensures widgets update during preview mode (mock source)
        return self.refresh_if_visible()

    def refresh_if_visible(self) -> bool:
        """Refresh widgets when global widget visibility allows it."""

        if not self._visibility_read.global_visible():
            return False
        return self.refresh()

    def refresh(self) -> bool:
        """Refresh widgets once."""

        if self._refreshing:
            return False
        self._refreshing = True
        try:
            self._records_refresh.refresh()
        finally:
            self._refreshing = False
        return True

    def _on_visibility_event(self, _event: Event) -> None:
        self.refresh()
