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

"""Widget flash effect state."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class FlashState:
    """Tick-driven flash state for one widget."""

    active: bool = False
    visible: bool = True
    target: str = "value"
    interval_ticks: int = 5
    counter: int = 0

    def set_active(self, *, interval_ticks: int, target: str) -> bool:
        """Activate flashing and return whether observable state changed."""

        safe_interval = max(1, int(interval_ticks))
        safe_target = target if target in ("value", "text", "widget", "border") else "value"
        changed = (
            not self.active
            or self.interval_ticks != safe_interval
            or self.target != safe_target
        )
        self.active = True
        self.interval_ticks = safe_interval
        self.target = safe_target
        return changed

    def reset(self) -> bool:
        """Reset flashing and return whether observable state changed."""

        changed = self.active or not self.visible or self.target != "value"
        self.active = False
        self.visible = True
        self.target = "value"
        self.counter = 0
        return changed

    def tick(self) -> bool:
        """Advance the flash clock and return whether visibility changed."""

        if not self.active:
            return False
        self.counter += 1
        if self.counter < self.interval_ticks:
            return False
        self.counter = 0
        self.visible = not self.visible
        return True


class FlashCapability:
    """Manage flash effect state for hosted widgets."""

    def __init__(self) -> None:
        self._states: dict[str, FlashState] = {}

    def set_flash(self, widget_key: str, *, active: bool, interval_ticks: int = 5, target: str = "value") -> bool:
        """Update flash state for one widget and return whether it changed."""

        state = self._states.setdefault(widget_key, FlashState())
        if active:
            return state.set_active(interval_ticks=interval_ticks, target=target)
        return state.reset()

    def state(self, widget_key: str) -> FlashState:
        """Return flash state for one widget."""

        return self._states.setdefault(widget_key, FlashState())

    def remove(self, widget_key: str) -> bool:
        """Remove one widget state."""

        return self._states.pop(widget_key, None) is not None

    def tick(self) -> list[str]:
        """Advance all active flash states and return changed widget keys."""

        changed: list[str] = []
        for widget_key, state in self._states.items():
            if state.tick():
                changed.append(widget_key)
        return changed
