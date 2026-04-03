"""Statusbar API for QML-facing statusbar contributions."""

from __future__ import annotations

from PySide6.QtCore import Property, QObject, Signal

from runtime_schema import Event, EventBus, EventType


class StatusbarApi(QObject):
    """QML-facing statusbar contribution model derived from runtime events."""

    statusbarItemsChanged = Signal()

    def __init__(self, event_bus: EventBus, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._event_bus = event_bus
        self._statusbar_left: list[dict] = []
        self._statusbar_right: list[dict] = []
        self._subscribe_to_events()

    def _subscribe_to_events(self) -> None:
        self._event_bus.on(EventType.STATUSBAR_REGISTERED, self._on_statusbar_registered, replay_history=True)

    def _on_statusbar_registered(self, event: Event) -> None:
        data = event.data
        item = {
            "icon": data.icon,
            "text": data.text,
            "tooltip": data.tooltip,
            "action": data.action,
        }
        if data.side == "left":
            self._statusbar_left.append(item)
        else:
            self._statusbar_right.append(item)
        self.statusbarItemsChanged.emit()

    @Property(list, notify=statusbarItemsChanged)
    def leftItems(self) -> list[dict]:
        return self._statusbar_left

    @Property(list, notify=statusbarItemsChanged)
    def rightItems(self) -> list[dict]:
        return self._statusbar_right
