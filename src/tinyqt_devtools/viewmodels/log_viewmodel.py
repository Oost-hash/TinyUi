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

from typing import TYPE_CHECKING, Callable

from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtQml import QmlElement, QmlSingleton

from tinyruntime_schema import LogInspector, LogRecordEntry

if TYPE_CHECKING:
    from tinyruntime import CoreRuntime, SchemaChangeEvent

QML_IMPORT_NAME = "TinyDevTools"
QML_IMPORT_MAJOR_VERSION = 1


@QmlElement
@QmlSingleton
class LogViewModel(QObject):
    """Exposes Python log output to QML.

    Connect to ``recordAdded(time, level, name, message)`` in QML.
    Call ``clear()`` to reset the console.
    """

    # time, level, logger name, message
    recordAdded = Signal(str, str, str, str)
    cleared     = Signal()

    def __init__(
        self,
        core: "CoreRuntime",
        inspector: LogInspector,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._core = core
        self._inspector = inspector
        self._unsubscribe_schema: Callable[[], None] = core.subscribe_schema_changes(
            self._on_schema_change,
            schema_id="tinyruntime.schema",
        )
        self.destroyed.connect(lambda *_: self.shutdown())

    def _on_record(self, entry: LogRecordEntry) -> None:
        try:
            self.recordAdded.emit(entry.time, entry.level, entry.name, entry.message)
        except RuntimeError:
            self.shutdown()

    def _on_schema_change(self, event: "SchemaChangeEvent") -> None:
        if event.change_key == "log.record" and isinstance(event.payload, LogRecordEntry):
            self._on_record(event.payload)
            return
        if event.change_key == "log.clear":
            self.cleared.emit()

    @Slot()
    def replay(self) -> None:
        for entry in self._inspector.records():
            self._on_record(entry)

    @Slot()
    def clear(self) -> None:
        self._inspector.clear()
        self._core.publish_schema_change(
            "tinyruntime.schema",
            producer="tinyqt_devtools.log_view_model",
            change_key="log.clear",
        )

    def shutdown(self) -> None:
        self._unsubscribe_schema()
