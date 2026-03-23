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

Thresholds are sorted ascending. The last entry whose value <= current wins.

Example for fuel (liters):
    ThresholdEntry(0.0, "#FF4444")   # red   — fuel >= 0
    ThresholdEntry(2.0, "#FF8C00")   # orange — fuel >= 2
    ThresholdEntry(5.0, "#E0E0E0")   # white  — fuel >= 5

    evaluate(thresholds, 1.5)  → "#FF4444"  (red)
    evaluate(thresholds, 3.0)  → "#FF8C00"  (orange)
    evaluate(thresholds, 10.0) → "#E0E0E0"  (white)
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ThresholdEntry:
    value: float
    color: str


def evaluate(thresholds: list[ThresholdEntry], value: float) -> str | None:
    """Return the color for the current value, or None if thresholds is empty."""
    if not thresholds:
        return None
    result: str | None = None
    for entry in sorted(thresholds, key=lambda e: e.value):
        if value >= entry.value:
            result = entry.color
    return result
