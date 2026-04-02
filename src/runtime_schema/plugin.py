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

"""Plugin schema definitions - states, events, and data classes."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto


class PluginState(Enum):
    """Plugin lifecycle states."""
    DISABLED = auto()    # Plugin is disabled
    ENABLING = auto()    # User enabled, preparing to load
    LOADING = auto()     # Importing plugin module
    ACTIVE = auto()      # Plugin is running
    UNLOADING = auto()   # Deactivating, cleaning up
    ERROR = auto()       # Error occurred during lifecycle


# Event data types for plugin events

@dataclass(frozen=True)
class PluginStateData:
    """Data for plugin.state_changed event."""
    plugin_id: str
    old_state: str
    new_state: str


@dataclass(frozen=True)
class PluginActivatedData:
    """Data for plugin.activated event."""
    plugin_id: str


@dataclass(frozen=True)
class PluginDeactivatedData:
    """Data for plugin.deactivated event."""
    plugin_id: str


@dataclass(frozen=True)
class PluginErrorData:
    """Data for plugin.error event."""
    plugin_id: str
    error_message: str
