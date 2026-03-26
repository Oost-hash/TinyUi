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
"""Declarative settings schema contracts shared by plugins and the host UI."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class SettingsSpec:
    """Declares one setting that a plugin or host surface exposes."""

    key: str
    label: str
    type: str
    default: Any
    description: str = ""
    options: list[str] = field(default_factory=list)
    section: str = ""
    min: float | None = None
    max: float | None = None
    step: float | None = None
