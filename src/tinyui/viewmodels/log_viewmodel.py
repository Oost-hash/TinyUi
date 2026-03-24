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

"""LogViewModel — bridges Python logging to QML via a Signal per log line."""

from __future__ import annotations

import logging

from PySide6.QtCore import QObject, Signal, Slot


class _QtLogHandler(logging.Handler):
    """Logging handler that calls a callback for each log record."""

    def __init__(self, callback):
        super().__init__()
        self._callback = callback

    def emit(self, record: logging.LogRecord) -> None:
        if self._callback is None:
            return
        try:
            import time as _time
            t = _time.strftime("%H:%M:%S", _time.localtime(record.created))
            ms = int(record.msecs)
            self._callback(f"{t}.{ms:03d}", record.levelname, record.name,
                           record.getMessage())
        except Exception:
            self.handleError(record)


class LogViewModel(QObject):
    """Exposes Python log output to QML.

    Connect to ``recordAdded(time, level, name, message)`` in QML.
    Call ``clear()`` to reset the console.
    """

    # time, level, logger name, message
    recordAdded = Signal(str, str, str, str)
    cleared     = Signal()

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)

        self._handler = _QtLogHandler(self.recordAdded.emit)
        self._handler.setLevel(logging.DEBUG)  # capture everything the root passes
        logging.getLogger().addHandler(self._handler)

    @Slot()
    def clear(self) -> None:
        self.cleared.emit()

    def shutdown(self) -> None:
        logging.getLogger().removeHandler(self._handler)
        self._handler._callback = None
