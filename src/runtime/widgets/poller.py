"""Polling helpers for runtime-owned widget refresh events."""

from __future__ import annotations

from PySide6.QtCore import QCoreApplication, QObject, QTimer

from runtime_schema import EventBus, EventType, WidgetRuntimeUpdatedData


class WidgetRuntimePoller(QObject):
    """Publish periodic widget runtime refresh events."""

    def __init__(
        self,
        event_bus: EventBus,
        *,
        interval_ms: int = 1000,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._event_bus = event_bus
        self._timer = QTimer(self)
        self._timer.setInterval(interval_ms)
        self._timer.timeout.connect(self._emit_poll_event)

    def start(self) -> None:
        """Start polling when a Qt application loop is available."""

        if QCoreApplication.instance() is None or self._timer.isActive():
            return
        self._timer.start()

    def stop(self) -> None:
        """Stop polling if it is active."""

        if self._timer.isActive():
            self._timer.stop()

    def _emit_poll_event(self) -> None:
        self._event_bus.emit_typed(
            EventType.WIDGET_RUNTIME_UPDATED,
            WidgetRuntimeUpdatedData(reason="game_detection_poll"),
        )
