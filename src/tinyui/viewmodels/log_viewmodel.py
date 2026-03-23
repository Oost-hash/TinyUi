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
    """Logging handler that calls a callback for each formatted record."""

    def __init__(self, callback):
        super().__init__()
        self._callback = callback

    def emit(self, record: logging.LogRecord) -> None:
        try:
            self._callback(self.format(record))
        except Exception:
            self.handleError(record)


class LogViewModel(QObject):
    """Exposes Python log output to QML.

    Connect to ``lineAdded(str)`` in QML to receive new log lines.
    Call ``clear()`` to reset the console.
    """

    lineAdded = Signal(str)
    cleared   = Signal()

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)

        self._handler = _QtLogHandler(self.lineAdded.emit)
        self._handler.setFormatter(logging.Formatter(
            "%(asctime)s %(levelname)-7s  %(name)s: %(message)s",
            datefmt="%H:%M:%S",
        ))
        logging.getLogger().addHandler(self._handler)

    @Slot()
    def clear(self) -> None:
        self.cleared.emit()

    def shutdown(self) -> None:
        logging.getLogger().removeHandler(self._handler)
