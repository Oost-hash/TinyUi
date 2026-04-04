"""Settings write capability."""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import QObject, Slot

from runtime.runtime import Runtime


class SettingsWrite(QObject):
    """QML-facing write surface for settings."""

    def __init__(self, runtime: Runtime, settings_read: Any | None = None, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._runtime = runtime
        self._settings_read = settings_read

    @Slot(str, str, str, result=bool)
    def setString(self, namespace: str, key: str, value: str) -> bool:
        registry = self._runtime.settings
        if registry is None:
            return False
        registry.set(namespace, key, value)
        registry.save(namespace)
        if self._settings_read is not None and hasattr(self._settings_read, "refresh"):
            self._settings_read.refresh()
        return True
