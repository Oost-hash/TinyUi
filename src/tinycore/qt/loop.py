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
"""PollLoop — central QTimer-based tick loop.

tinycore owns the loop. Anything that implements Tickable can register here.
tinywidgets registers its runners; the loop drives them without knowing what they are.
"""

from __future__ import annotations

from PySide6.QtCore import QTimer

from tinycore.poll.tickable import Tickable


class PollLoop:
    """Drives all registered Tickables at a fixed interval via QTimer.

    Usage:
        loop = PollLoop(interval_ms=100)
        loop.register(my_runner)
        loop.start()
        # ... app runs ...
        loop.stop()
    """

    def __init__(self, interval_ms: int = 100) -> None:
        self._tickables: list[Tickable] = []
        self._interval_ms = interval_ms
        self._timer = QTimer()
        self._timer.setInterval(interval_ms)
        self._timer.timeout.connect(self._tick)

    @property
    def interval_ms(self) -> int:
        return self._interval_ms

    def register(self, tickable: Tickable) -> None:
        """Add a Tickable to the loop."""
        self._tickables.append(tickable)

    def start(self) -> None:
        """Start polling."""
        self._timer.start()

    def stop(self) -> None:
        """Stop polling."""
        self._timer.stop()

    def _tick(self) -> None:
        for tickable in self._tickables:
            tickable.tick()
