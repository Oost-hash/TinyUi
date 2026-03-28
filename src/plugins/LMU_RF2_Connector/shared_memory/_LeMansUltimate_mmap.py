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

"""
LMU memory map control.

Based on pyLMUSharedMemory / TinyPedal by S.Victor:
  https://github.com/TinyPedal/pyLMUSharedMemory

Memory map control by S.Victor; cross-platform Linux support by Bernat.
"""

from __future__ import annotations

import ctypes
import logging
import mmap
import platform
from collections.abc import Callable
from typing import cast

from . import _LeMansUltimate_data as lmu_data
from ._LeMansUltimate_data import LMUConstants

PLATFORM = platform.system()
MAX_VEHICLES = LMUConstants.MAX_MAPPED_VEHICLES
INVALID_INDEX = -1


def get_root_logger_name():
    """Get root logger name"""
    for logger_name in logging.root.manager.loggerDict:
        return logger_name
    return __name__


logger = logging.getLogger(get_root_logger_name())


def platform_mmap(name: str, size: int) -> mmap.mmap:
    """Platform memory mapping"""
    if PLATFORM == "Windows":
        return windows_mmap(name, size)
    return linux_mmap(name, size)


def windows_mmap(name: str, size: int) -> mmap.mmap:
    """Windows mmap"""
    return mmap.mmap(-1, size, name)  # type: ignore[arg-type]  # tagname: str, stubs are wrong


def linux_mmap(name: str, size: int) -> mmap.mmap:
    """Linux mmap - read data from '/dev/shm/filename' if available"""
    file = open("/dev/shm/" + name, "a+b")
    if file.tell() == 0:
        file.write(b"\0" * size)
        file.flush()
    return mmap.mmap(file.fileno(), size)


class MMapControl:
    """Memory map control"""

    __slots__ = (
        "_mmap_name",
        "_mmap_buffer",
        "_struct",
        "_buffer",
        "_realtime",
        "update",
        "data",
    )

    _mmap_name: str
    _mmap_buffer: mmap.mmap | None
    _struct: type[ctypes.Structure]
    _buffer: bytearray
    _realtime: lmu_data.LMUObjectOut | None
    update: Callable[[], None] | None
    data: ctypes.Structure | None

    def __init__(self, mmap_name: str, data_struct: type[ctypes.Structure]) -> None:
        """Initialize memory map setting

        Args:
            mmap_name: mmap filename.
            data_struct: ctypes data structure, ex. lmu_data.LMUObjectOut.
        """
        self._mmap_name = mmap_name
        self._mmap_buffer = None
        self._struct = data_struct
        self._buffer = bytearray()
        self._realtime = None
        self.update = None
        self.data = None

    def __del__(self):
        logger.info("sharedmemory: GC: MMap %s", self._mmap_name)

    def create(self, access_mode: int = 0) -> None:
        """Create mmap instance & initial accessible copy

        Args:
            access_mode: 0 = copy access, 1 = direct access.
        """
        self._mmap_buffer = platform_mmap(
            name=self._mmap_name,
            size=ctypes.sizeof(self._struct),
        )

        if access_mode:
            self.data = self._struct.from_buffer(self._mmap_buffer)
            self.update = self.__buffer_share
        else:
            self._buffer[:] = self._mmap_buffer
            self._realtime = cast(lmu_data.LMUObjectOut, self._struct.from_buffer(self._mmap_buffer))
            self.data = self._struct.from_buffer(self._buffer)
            self.update = self.__buffer_copy

        mode = "Direct" if access_mode else "Copy"
        logger.info("sharedmemory: ACTIVE: %s (%s Access)", self._mmap_name, mode)

    def close(self) -> None:
        """Close memory mapping

        Create a final accessible mmap data copy before closing mmap instance.
        """
        assert self._mmap_buffer is not None
        self.data = self._struct.from_buffer_copy(self._mmap_buffer)
        self._realtime = None
        try:
            self._mmap_buffer.close()
            logger.info("sharedmemory: CLOSED: %s", self._mmap_name)
        except BufferError:
            logger.error("sharedmemory: buffer error while closing %s", self._mmap_name)
        self.update = None  # unassign update method (for proper garbage collection)

    def __buffer_share(self) -> None:
        """Share buffer access, may result data desync"""

    def __buffer_copy(self) -> None:
        """Copy buffer access, helps avoid data desync"""
        assert self._realtime is not None
        assert self._mmap_buffer is not None
        # Check if game updating data
        if (
            self._realtime.generic.events.SME_UPDATE_SCORING
            or self._realtime.generic.events.SME_UPDATE_TELEMETRY
        ) and (
            self._realtime.scoring.scoringInfo.mNumVehicles
            == self._realtime.telemetry.activeVehicles
        ):
            self._buffer[:] = self._mmap_buffer


def test_api():
    """API test run"""
    # Add logger
    test_handler = logging.StreamHandler()
    logger.setLevel(logging.INFO)
    logger.addHandler(test_handler)

    # Test run
    SEPARATOR = "=" * 50
    print("Test API - Direct Access")
    info = MMapControl(LMUConstants.LMU_SHARED_MEMORY_FILE, lmu_data.LMUObjectOut)
    info.create(1)
    assert info.update is not None
    info.update()

    print(SEPARATOR)
    print("Test API - Close")
    info.close()

    print(SEPARATOR)
    print("Test API - Copy Access")
    info.create(0)
    assert info.update is not None
    info.update()

    print(SEPARATOR)
    print("Test API - Read")
    data = cast(lmu_data.LMUObjectOut, info.data)
    version = data.generic.gameVersion
    track = data.scoring.scoringInfo.mTrackName.decode()
    vehicle = data.telemetry.telemInfo[0].mVehicleName.decode()
    total = data.scoring.scoringInfo.mNumVehicles
    print(f"version: {version if version else 'not running'}")
    print(f"track name: {track if version else 'not running'}")
    print(f"vehicle name: {vehicle if version else 'not running'}")
    print(f"total cars: {total if version else 'not running'}")

    print(SEPARATOR)
    info.close()


if __name__ == "__main__":
    test_api()
