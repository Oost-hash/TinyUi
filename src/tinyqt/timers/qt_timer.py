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
"""Qt-backed timer adapter for runtime-owned interval work."""

from __future__ import annotations

from typing import Callable

from PySide6.QtCore import QObject, QTimer


class RuntimeQtTimer:
    """Wrap a QTimer behind a small runtime-owned scheduling surface."""

    def __init__(
        self,
        *,
        interval_ms: int,
        callback: Callable[[], None],
        parent: QObject | None = None,
        single_shot: bool = False,
    ) -> None:
        self._interval_ms = interval_ms
        self._timer = QTimer(parent)
        self._timer.setSingleShot(single_shot)
        self._timer.setInterval(interval_ms)
        self._timer.timeout.connect(callback)

    @property
    def interval_ms(self) -> int:
        return self._interval_ms

    def start(self) -> None:
        self._timer.start()

    def stop(self) -> None:
        self._timer.stop()

    def is_active(self) -> bool:
        return self._timer.isActive()
