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
"""FlashState — tick-driven blink for critical widget values.

Driven by the PollLoop (100 ms ticks). Default: toggles every 5 ticks = 500 ms.
"""

from __future__ import annotations


class FlashState:
    """Toggles visibility at a fixed tick interval.

    Call tick() each PollLoop cycle.
    Read visible to decide whether the widget should render.
    Call reset() when the flash condition is no longer met.
    """

    def __init__(self, interval_ticks: int = 5) -> None:
        self._interval = interval_ticks
        self._counter  = 0
        self._visible  = True

    def tick(self) -> None:
        self._counter += 1
        if self._counter >= self._interval:
            self._counter = 0
            self._visible = not self._visible

    @property
    def interval(self) -> int:
        return self._interval

    @interval.setter
    def interval(self, v: int) -> None:
        self._interval = max(1, v)

    @property
    def visible(self) -> bool:
        return self._visible

    def reset(self) -> None:
        """Call when flash condition is no longer active."""
        self._counter = 0
        self._visible = True
