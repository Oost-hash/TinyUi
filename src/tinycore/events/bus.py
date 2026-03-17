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
"""EventBus — string-keyed pub/sub."""

from __future__ import annotations

from typing import Any, Callable


class EventBus:
    """Simple string-keyed event bus with on/emit/once."""

    def __init__(self):
        self._listeners: dict[str, list[Callable]] = {}

    def on(self, event: str, callback: Callable[..., Any]) -> Callable:
        """Subscribe to an event. Returns an unsubscribe function."""
        self._listeners.setdefault(event, []).append(callback)

        def unsubscribe():
            self._listeners[event].remove(callback)

        return unsubscribe

    def once(self, event: str, callback: Callable[..., Any]) -> Callable:
        """Subscribe to an event, auto-unsubscribe after first fire."""

        def wrapper(*args: Any, **kwargs: Any) -> Any:
            unsubscribe()
            return callback(*args, **kwargs)

        unsubscribe = self.on(event, wrapper)
        return unsubscribe

    def emit(self, event: str, *args: Any, **kwargs: Any) -> None:
        """Fire an event. All listeners are called in registration order."""
        for callback in list(self._listeners.get(event, [])):
            callback(*args, **kwargs)
