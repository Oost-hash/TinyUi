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
"""Shared LMU connector helpers and imports."""

from __future__ import annotations

from plugins.lmu_connector.pyLMUSharedMemory import lmu_data
from plugins.lmu_connector.pyLMUSharedMemory.lmu_data import LMUConstants
from plugins.lmu_connector.pyLMUSharedMemory.lmu_mmap import MMapControl

_KELVIN = 273.15

_SESSION_NAMES = {
    0: "test",
    1: "practice",
    2: "qualify",
    3: "warmup",
    4: "race",
}


def decode_bytes(raw: bytes) -> str:
    """Decode LMU shared memory bytes into text."""
    return raw.rstrip(b"\x00").decode("utf-8", errors="replace")
