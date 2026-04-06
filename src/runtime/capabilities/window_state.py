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

"""Window state capability — manages runtime window state tracking."""

from __future__ import annotations

from typing import TYPE_CHECKING

from runtime.ui import WindowRuntimeStatus, WindowRuntimeRecord
from runtime_schema import EventType, WindowRuntimeUpdatedData

if TYPE_CHECKING:
    from runtime.runtime import Runtime


class WindowStateCapability:
    """Manages window runtime state.

    Tracks window lifecycle states (opening, open, hidden, closing, closed)
    and errors for all managed windows.
    """

    def __init__(self) -> None:
        self._runtime: Runtime | None = None
        self._states: dict[str, WindowRuntimeStatus] = {}
        self._errors: dict[str, str] = {}

    @property
    def name(self) -> str:
        """Unique capability name."""
        return "window_state"

    def attach(self, runtime: Runtime) -> None:
        """Attach to runtime — called on registration."""
        self._runtime = runtime

    def qml_interface(self) -> None:
        """No QML interface for this capability."""
        return None

    def _emit_update(self, reason: str = "runtime") -> None:
        """Emit window runtime updated event."""
        if self._runtime is not None:
            self._runtime.events.emit_typed(
                EventType.WINDOW_RUNTIME_UPDATED,
                WindowRuntimeUpdatedData(reason=reason)
            )

    def _set_status(self, window_id: str, status: WindowRuntimeStatus, reason: str = "") -> None:
        """Set window status and emit update."""
        self._states[window_id] = status
        if status != WindowRuntimeStatus.ERROR:
            self._errors.pop(window_id, None)
        self._emit_update(reason if reason else status.value)

    def mark_opening(self, window_id: str) -> None:
        """Record that a window handoff to ui_api has started."""
        self._set_status(window_id, WindowRuntimeStatus.OPENING, "opening")

    def mark_open(self, window_id: str) -> None:
        """Record that a window is open."""
        self._set_status(window_id, WindowRuntimeStatus.OPEN, "open")

    def mark_hidden(self, window_id: str) -> None:
        """Record that a window remains hosted but hidden."""
        self._set_status(window_id, WindowRuntimeStatus.HIDDEN, "hidden")

    def mark_closing(self, window_id: str) -> None:
        """Record that a window is in the shutdown or close handoff."""
        self._set_status(window_id, WindowRuntimeStatus.CLOSING, "closing")

    def mark_closed(self, window_id: str) -> None:
        """Record that a window has been closed."""
        self._set_status(window_id, WindowRuntimeStatus.CLOSED, "closed")

    def mark_error(self, window_id: str, message: str) -> None:
        """Record that a window failed to open or close correctly."""
        self._errors[window_id] = message
        self._set_status(window_id, WindowRuntimeStatus.ERROR, "error")

    def get_status(self, window_id: str) -> WindowRuntimeStatus:
        """Get current status for a window."""
        return self._states.get(window_id, WindowRuntimeStatus.CLOSED)

    def get_error(self, window_id: str) -> str | None:
        """Get error message for a window, if any."""
        return self._errors.get(window_id)

    def project_records(
        self,
        plugins: dict,
        window_states: dict[str, WindowRuntimeStatus] | None = None,
        window_errors: dict[str, str] | None = None,
    ) -> list[WindowRuntimeRecord]:
        """Project runtime-owned records for manifest-declared windows.

        This replaces the old project_window_records function.
        """
        from runtime.ui import project_window_records

        return project_window_records(
            plugins,
            window_states=self._states,
            window_errors=self._errors,
        )
