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

"""Menu schema definitions."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MenuItem:
    """A menu item."""
    label: str
    action: str
    source: str = "host"   # "host" | "plugin"


@dataclass(frozen=True)
class MenuSeparator:
    """A menu separator."""
    source: str = "host"   # "host" | "plugin"


MenuEntry = MenuItem | MenuSeparator
