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
"""Diagnostics buffer for captured log records."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class LogRecordEntry:
    """One captured log record."""

    time: str
    level: str
    name: str
    message: str


class _InspectorLogHandler(logging.Handler):
    """Logging handler that forwards records into the log inspector."""

    def __init__(self, callback: Callable[[LogRecordEntry], None]) -> None:
        super().__init__()
        self._callback = callback

    def emit(self, record: logging.LogRecord) -> None:
        try:
            created = time.localtime(record.created)
            stamp = time.strftime("%H:%M:%S", created)
            entry = LogRecordEntry(
                time=f"{stamp}.{int(record.msecs):03d}",
                level=record.levelname,
                name=record.name,
                message=record.getMessage(),
            )
            self._callback(entry)
        except Exception:
            self.handleError(record)


class LogInspector:
    """Captures Python log records for Dev Tools and diagnostics."""

    def __init__(self, max_records: int = 2000) -> None:
        self._max_records = max_records
        self._records: list[LogRecordEntry] = []
        self._listeners: list[Callable[[LogRecordEntry], None]] = []
        self._handler = _InspectorLogHandler(self._append)
        self._handler.setLevel(logging.DEBUG)
        logging.getLogger().addHandler(self._handler)

    def _append(self, entry: LogRecordEntry) -> None:
        self._records.append(entry)
        if len(self._records) > self._max_records:
            del self._records[: -self._max_records]
        for listener in list(self._listeners):
            listener(entry)

    def records(self) -> list[LogRecordEntry]:
        """Return the currently buffered log records."""
        return list(self._records)

    def clear(self) -> None:
        """Clear buffered log records."""
        self._records.clear()

    def subscribe(self, listener: Callable[[LogRecordEntry], None]) -> None:
        """Subscribe to future log records."""
        self._listeners.append(listener)

    def unsubscribe(self, listener: Callable[[LogRecordEntry], None]) -> None:
        """Unsubscribe from future log records."""
        if listener in self._listeners:
            self._listeners.remove(listener)

    def shutdown(self) -> None:
        """Detach the inspector from root logging."""
        logging.getLogger().removeHandler(self._handler)
        self._listeners.clear()
