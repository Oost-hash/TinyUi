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

"""Shared source protocol for the consolidated connector family."""

from __future__ import annotations

from abc import ABC, abstractmethod

from .telemetry import TelemetryReader


class ConnectorSource(ABC):
    """Common lifecycle and metadata contract for family sources."""

    name: str
    kind: str
    game: str
    description: str

    @abstractmethod
    def open(self) -> None:
        """Allocate or activate the source."""

    @abstractmethod
    def close(self) -> None:
        """Release source resources."""

    @abstractmethod
    def update(self) -> None:
        """Advance the source one tick."""

    @property
    @abstractmethod
    def reader(self) -> TelemetryReader:
        """Expose the shared telemetry reader surface for the source."""
