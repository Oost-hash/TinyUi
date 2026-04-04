"""Application action API exposed to QML."""

from __future__ import annotations

from typing import Callable

from PySide6.QtCore import QObject, Slot


class AppActions(QObject):
    """Dispatch named app actions from QML into Python handlers."""

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
