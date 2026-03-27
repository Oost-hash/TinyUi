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

"""Runtime-owned Qt update loop for recurring host ticks."""

from __future__ import annotations

from .qt_timer import RuntimeQtTimer
from .tickables import Tickable


class RuntimeUpdateLoop:
    """Drive registered update participants at a fixed interval via a runtime-owned Qt timer."""

    def __init__(self, interval_ms: int = 100) -> None:
        self._tickables: list[Tickable] = []
        self._timer = RuntimeQtTimer(interval_ms=interval_ms, callback=self._tick)

    @property
    def interval_ms(self) -> int:
        return self._timer.interval_ms

    def register(self, tickable: Tickable) -> None:
        self._tickables.append(tickable)

    def start(self) -> None:
        self._timer.start()

    def stop(self) -> None:
        self._timer.stop()

    def _tick(self) -> None:
        for tickable in self._tickables:
            tickable.tick()
