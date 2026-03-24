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
"""Threshold evaluation.

Each threshold defines the UPPER BOUND of a color band.
Sorted ascending — first entry where value <= threshold wins.
Values above all thresholds return None (caller uses the default/widget color).

Example for fuel (liters):
    ThresholdEntry(10.0, "#FF4444")  # red    — fuel <= 10
    ThresholdEntry(30.0, "#FF8C00")  # orange — fuel <= 30
    # no entry needed for normal (> 30) — returns None → default color

    evaluate(thresholds, 5.0)  → "#FF4444"  (red)
    evaluate(thresholds, 15.0) → "#FF8C00"  (orange)
    evaluate(thresholds, 50.0) → None       (default)
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ThresholdEntry:
    value:        float
    color:        str
    flash:        bool = False
    flash_speed:  int  = 5        # PollLoop ticks per toggle (1 tick = 100 ms)
    flash_target: str  = "value"  # "value" | "text" | "widget"


def evaluate(thresholds: list[ThresholdEntry], value: float) -> str | None:
    """Return the color for the current value, or None if above all thresholds."""
    for entry in sorted(thresholds, key=lambda e: e.value):
        if value <= entry.value:
            return entry.color
    return None
