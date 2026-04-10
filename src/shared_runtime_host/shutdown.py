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

"""Shared shutdown helpers for QML runtime hosts."""

from __future__ import annotations

from collections.abc import Callable

from runtimeV2.capabilities.runtime_shutdown import RuntimeShutdown
from runtimeV2.contracts import EventType
from runtimeV2.events.startup_shutdown.startup import EventsStartupResult
from runtimeV2.runtime import RuntimeV2


class QmlRuntimeHostShutdown:
    """Keep one QML runtime host aligned with runtime shutdown intent."""

    def __init__(self, runtime: RuntimeV2, close_host: Callable[[], None]) -> None:
        self._runtime = runtime
        self._close_host = close_host
        self._closed = False

    def attach(self, app) -> None:
        """Attach runtime and application shutdown hooks."""

        events = self._runtime.domain_result("events", EventsStartupResult)
        events.bus.on(EventType.RUNTIME_SHUTDOWN, self._on_runtime_shutdown)
        app.aboutToQuit.connect(self._on_app_about_to_quit)

    def close_host(self) -> None:
        """Close the hosted QML resources once."""

        if self._closed:
            return
        self._closed = True
        self._close_host()

    def _on_runtime_shutdown(self, _event) -> None:
        self.close_host()

    def _on_app_about_to_quit(self) -> None:
        shutdown = self._runtime.capability("shutdown", RuntimeShutdown)
        shutdown.begin_shutdown("app_quit")
        self.close_host()

