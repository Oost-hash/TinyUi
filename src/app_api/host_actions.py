"""QML-facing action dispatcher for host windows."""

from __future__ import annotations

from typing import Callable

from PySide6.QtCore import QObject, Slot


class HostActions(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._handlers: dict[str, Callable[[], None]] = {}

    def register(self, action: str, handler: Callable[[], None]) -> None:
        self._handlers[action] = handler

    @Slot(str)
    def trigger(self, action: str) -> None:
        handler = self._handlers.get(action)
        if handler is not None:
            handler()
