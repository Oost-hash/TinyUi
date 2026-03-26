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

"""Signal primitives for the mock telemetry source."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Signal:
    minimum: float
    maximum: float
    step: float
    value: float
    direction: float = 1.0

    def ping_pong(self) -> float:
        self.value += self.step * self.direction
        if self.value >= self.maximum:
            self.value = self.maximum
            self.direction = -1.0
        elif self.value <= self.minimum:
            self.value = self.minimum
            self.direction = 1.0
        return self.value

    def descend_wrap(self) -> float:
        self.value -= self.step
        if self.value < self.minimum:
            self.value = self.maximum
        return self.value
