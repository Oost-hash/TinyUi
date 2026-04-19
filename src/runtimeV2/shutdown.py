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

"""Runtime V2 shutdown state and orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from runtimeV2.events.contracts import EventType
from runtimeV2.schemas.events import RuntimeShutdownData

if TYPE_CHECKING:
    from runtimeV2.runtime import RuntimeV2


@dataclass
class RuntimeShutdownState:
    """Mutable runtime shutdown state."""

    requested: bool = False
    reason: str = ""


class RuntimeShutdownController:
    """Own runtime shutdown intent and stop-hook orchestration."""

    def __init__(self, runtime: RuntimeV2) -> None:
        self._runtime = runtime
        self._state = RuntimeShutdownState()

    def shutdown_requested(self) -> bool:
        """Return whether runtime shutdown was already requested."""

        return self._state.requested

    def shutdown_reason(self) -> str:
        """Return the current shutdown reason."""

        return self._state.reason

    def begin_shutdown(self, reason: str = "app_quit") -> bool:
        """Request runtime shutdown once and run stop hooks."""

        if self._state.requested:
            return False

        self._state.requested = True
        self._state.reason = reason
        self._emit_runtime_shutdown(reason)
        self._run_stop_hooks()
        return True

    def _emit_runtime_shutdown(self, reason: str) -> None:
        try:
            from runtimeV2.events.startup_shutdown.startup import EventsStartupResult

            events = self._runtime.domain_result("events", EventsStartupResult)
        except KeyError:
            return

        events.bus.emit_typed(
            EventType.RUNTIME_SHUTDOWN,
            RuntimeShutdownData(reason=reason),
            source="runtimeV2",
        )

    def _run_stop_hooks(self) -> None:
        for owner in self._runtime.stop_hook_owner_order():
            hooks = list(reversed(self._runtime.stop_hooks(owner)))
            for hook in hooks:
                hook()

            self._runtime.mark_domain_stopped(owner)

