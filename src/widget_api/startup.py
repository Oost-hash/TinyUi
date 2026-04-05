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

"""Widget API domain startup."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from widget_api.defaults import create_default_widget_registry
from widget_api.registry import WidgetRegistry

if TYPE_CHECKING:
    from runtime_schema import EventBus
    from runtime_schema.startup import StartupResult


@dataclass
class WidgetApiStartupResult:
    """Result of widget API domain startup."""

    registry: WidgetRegistry


# Module-level storage for startup result
_widget_api_result: WidgetApiStartupResult | None = None


def startup_widget_api(event_bus: EventBus | None = None) -> StartupResult:
    """Startup function for widget_api domain.
    
    Creates the widget registry with default widget definitions.
    
    Returns:
        StartupResult with ok=True on success.
    """
    from runtime_schema.startup import startup_ok, startup_error
    global _widget_api_result

    try:
        registry = create_default_widget_registry()
        _widget_api_result = WidgetApiStartupResult(registry=registry)
        return startup_ok()
    except Exception as e:
        _widget_api_result = None
        return startup_error(f"Widget API startup failed: {e}")


def get_widget_api_result() -> WidgetApiStartupResult | None:
    """Get the widget API startup result.
    
    Returns None if startup was not called or failed.
    """
    return _widget_api_result
