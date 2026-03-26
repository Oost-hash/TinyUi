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

"""Mock source wrapper for the consolidated connector family."""

from __future__ import annotations

from ...contracts.source import ConnectorSource
from ...contracts.telemetry import TelemetryReader
from .telemetry import MockTelemetryReader


class MockSource(ConnectorSource):
    """Telemetry-capable mock source that behaves like a normal family source."""

    name = "mock"
    kind = "mock"
    game = "mock"
    description = "Fake telemetry source used for development, preview, and demo flows."

    def __init__(self) -> None:
        self._reader = MockTelemetryReader()

    @property
    def min_val(self) -> float:
        return self._reader.min_val

    @property
    def max_val(self) -> float:
        return self._reader.max_val

    @property
    def step(self) -> float:
        return self._reader.step

    def configure(self, minimum: float, maximum: float, step: float) -> None:
        self._reader.configure(minimum, maximum, step)

    def open(self) -> None:
        self._reader.open()

    def close(self) -> None:
        self._reader.close()

    def update(self) -> None:
        self._reader.update()

    @property
    def reader(self) -> TelemetryReader:
        return self._reader
