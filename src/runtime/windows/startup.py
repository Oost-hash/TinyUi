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

"""Window runtime domain startup."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from runtime.windows.runtime import WindowRuntime
    from runtime_schema import EventBus
    from runtime_schema.startup import StartupResult


@dataclass
class WindowRuntimeStartupResult:
    """Result of window runtime startup."""

    window_runtime: WindowRuntime


# Module-level storage
_window_runtime_result: WindowRuntimeStartupResult | None = None


def startup_window_runtime(event_bus: EventBus) -> StartupResult:
    """Startup function for window runtime domain.

    Creates the WindowRuntime that tracks all window states.

    Args:
        event_bus: Event bus for window runtime events.

    Returns:
        StartupResult with ok=True on success.
    """
    from runtime_schema.startup import startup_ok, startup_error
    from runtime.windows.runtime import WindowRuntime
    global _window_runtime_result

    try:
        window_runtime = WindowRuntime(event_bus)
        _window_runtime_result = WindowRuntimeStartupResult(
            window_runtime=window_runtime,
        )
        return startup_ok()
    except Exception as e:
        _window_runtime_result = None
        return startup_error(f"Window runtime startup failed: {e}")


def get_window_runtime_result() -> WindowRuntimeStartupResult | None:
    """Get the window runtime startup result.

    Returns:
        WindowRuntimeStartupResult with window_runtime, or None if failed.
    """
    return _window_runtime_result
