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

"""Thin Qt adapter over the runtime log inspector."""

from __future__ import annotations

from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtQml import QmlElement

from tinycore.logging import LogInspector, LogRecordEntry

QML_IMPORT_NAME = "TinyDevTools"
QML_IMPORT_MAJOR_VERSION = 1


@QmlElement
class LogViewModel(QObject):
    """Exposes Python log output to QML.

    Connect to ``recordAdded(time, level, name, message)`` in QML.
    Call ``clear()`` to reset the console.
    """

    # time, level, logger name, message
    recordAdded = Signal(str, str, str, str)
    cleared     = Signal()

    def __init__(self, inspector: LogInspector, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._inspector = inspector
        self._inspector.subscribe(self._on_record)

    def _on_record(self, entry: LogRecordEntry) -> None:
        self.recordAdded.emit(entry.time, entry.level, entry.name, entry.message)

    @Slot()
    def replay(self) -> None:
        for entry in self._inspector.records():
            self._on_record(entry)

    @Slot()
    def clear(self) -> None:
        self._inspector.clear()
        self.cleared.emit()

    def shutdown(self) -> None:
        self._inspector.unsubscribe(self._on_record)
