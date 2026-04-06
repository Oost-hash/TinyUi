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

"""Contracts for runtime-owned window records."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class WindowRuntimeStatus(StrEnum):
    """Observable runtime status for one application window."""

    IDLE = "idle"
    OPENING = "opening"
    OPEN = "open"
    HIDDEN = "hidden"
    CLOSING = "closing"
    CLOSED = "closed"
    ERROR = "error"


@dataclass(frozen=True)
class WindowRuntimeRecord:
    """Projected runtime record for one application window."""

    window_id: str
    plugin_id: str
    window_role: str
    status: WindowRuntimeStatus
    visible: bool
    surface: str
    error_message: str = ""
