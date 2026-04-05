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

"""Events domain startup — creates the EventBus."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from runtime_schema import EventBus
    from runtime_schema.startup import StartupResult


# Module-level storage for startup result
_events_result: "EventBus | None" = None


def startup_events() -> "StartupResult":
    """Startup function for events domain.
    
    Creates the EventBus that all other domains use for communication.
    This must be the first startup step, as all other startups depend on it.
    
    Returns:
        StartupResult with ok=True on success.
    """
    from runtime_schema import EventBus
    from runtime_schema.startup import startup_ok, startup_error
    global _events_result

    try:
        event_bus = EventBus()
        _events_result = event_bus
        return startup_ok()
    except Exception as e:
        _events_result = None
        return startup_error(f"Events startup failed: {e}")


def get_events_result() -> "EventBus | None":
    """Get the EventBus created during startup.
    
    Returns None if startup was not called or failed.
    """
    return _events_result
