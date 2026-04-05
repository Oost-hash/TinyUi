"""Window read capability."""

from __future__ import annotations

from PySide6.QtCore import Property, QObject, Signal

from runtime.runtime import Runtime
from runtime_schema import EventBus, EventType


class WindowRead(QObject):
    """Expose runtime-owned window records to QML consumers."""

    windowsChanged = Signal()

    def __init__(self, runtime: Runtime, event_bus: EventBus, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._runtime = runtime
        self._event_bus = event_bus
        self._windows = self._build_windows()
        self._subscribe()

    def _subscribe(self) -> None:
        for event_type in (
            EventType.BOOT_READY,
            EventType.WINDOW_RUNTIME_UPDATED,
            EventType.RUNTIME_SHUTDOWN,
        ):
            self._event_bus.on(event_type, self._on_runtime_changed, replay_history=True)

    def _on_runtime_changed(self, _event) -> None:
        self.refresh()

    def _build_windows(self) -> list[dict[str, object]]:
        return [
            {
                "windowId": record.window_id,
                "pluginId": record.plugin_id,
                "windowRole": record.window_role,
                "status": record.status.value,
                "visible": record.visible,
                "surface": record.surface,
                "errorMessage": record.error_message,
            }
            for record in self._runtime.window_records()
        ]

    def refresh(self) -> None:
        self._windows = self._build_windows()
        self.windowsChanged.emit()

    def items(self) -> list[dict[str, object]]:
        return list(self._windows)

    @Property(list, notify=windowsChanged)
    def windows(self) -> list[dict[str, object]]:
        return list(self._windows)
