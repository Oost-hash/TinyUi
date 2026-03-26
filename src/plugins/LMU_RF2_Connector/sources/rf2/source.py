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

"""rFactor 2 source wrapper for the consolidated connector family."""

from __future__ import annotations

from ...contracts.source import ConnectorSource
from ...contracts.telemetry import TelemetryReader
from .telemetry import RF2TelemetryReader


class RF2LiveSource(ConnectorSource):
    """Live rFactor 2 shared-memory source for the connector family."""

    name = "rf2"
    kind = "shared-memory"
    game = "rf2"
    description = "Live rFactor 2 shared-memory telemetry source."

    def __init__(self) -> None:
        self._reader = RF2TelemetryReader()

    def open(self) -> None:
        self._reader.open()

    def close(self) -> None:
        self._reader.close()

    def update(self) -> None:
        self._reader.update()

    @property
    def reader(self) -> TelemetryReader:
        return self._reader
