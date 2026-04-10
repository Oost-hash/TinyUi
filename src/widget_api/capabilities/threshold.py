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

"""Widget threshold evaluation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ThresholdEntry:
    """Upper-bound threshold rule for one widget value."""

    value: float
    color: str
    flash: bool = False
    flash_speed: int = 5
    flash_target: str = "value"


@dataclass(frozen=True)
class ThresholdState:
    """Result of threshold evaluation for one widget."""

    active: bool
    color: str | None = None
    flash: bool = False
    flash_speed: int = 5
    flash_target: str = "value"


class ThresholdCapability:
    """Evaluate persistence-owned threshold rules for widget values."""

    def evaluate(self, thresholds: list[ThresholdEntry], value: float | None) -> ThresholdState:
        """Return the first upper-bound threshold state for the given value."""

        if value is None:
            return ThresholdState(active=False)
        for entry in sorted(thresholds, key=lambda item: item.value):
            if value <= entry.value:
                return ThresholdState(
                    active=True,
                    color=entry.color,
                    flash=entry.flash,
                    flash_speed=entry.flash_speed,
                    flash_target=entry.flash_target,
                )
        return ThresholdState(active=False)


def threshold_entries(raw_thresholds: object) -> list[ThresholdEntry]:
    """Parse persisted widget threshold config into entries."""

    if not isinstance(raw_thresholds, list):
        return []
    entries: list[ThresholdEntry] = []
    for raw in raw_thresholds:
        if not isinstance(raw, dict):
            continue
        entry = _threshold_entry(raw)
        if entry is not None:
            entries.append(entry)
    return entries


def numeric_value(value: object) -> float | None:
    """Convert a widget value to a threshold-comparable number."""

    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return None
    return None


def _threshold_entry(raw: dict[str, Any]) -> ThresholdEntry | None:
    try:
        value = float(raw["value"])
    except (KeyError, TypeError, ValueError):
        return None
    color = str(raw.get("color", "#E0E0E0"))
    flash_target = str(raw.get("flashTarget", raw.get("flash_target", "value")))
    return ThresholdEntry(
        value=value,
        color=color,
        flash=bool(raw.get("flash", False)),
        flash_speed=max(1, int(raw.get("flashSpeed", raw.get("flash_speed", 5)))),
        flash_target=flash_target if flash_target in ("value", "text", "widget") else "value",
    )
