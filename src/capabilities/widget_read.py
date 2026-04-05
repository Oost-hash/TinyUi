"""Widget read capability."""

from __future__ import annotations

from PySide6.QtCore import Property, QObject, Signal

from runtime.runtime import Runtime
from runtime_schema import EventBus, EventType


class WidgetRead(QObject):
    """Expose active runtime-owned widget records to QML consumers."""

    widgetsChanged = Signal()

    def __init__(self, runtime: Runtime, event_bus: EventBus, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._runtime = runtime
        self._event_bus = event_bus
        self._widgets = self._build_widgets()
        self._subscribe()

    def _subscribe(self) -> None:
        for event_type in (
            EventType.PLUGIN_STATE_CHANGED,
            EventType.PLUGIN_ERROR,
            EventType.UI_PLUGIN_SELECTED,
            EventType.CONNECTOR_SERVICE_REGISTERED,
            EventType.CONNECTOR_SERVICE_UNREGISTERED,
            EventType.CONNECTOR_SERVICE_UPDATED,
            EventType.RUNTIME_SHUTDOWN,
            EventType.WIDGET_RUNTIME_UPDATED,
        ):
            self._event_bus.on(event_type, self._on_runtime_changed, replay_history=True)

    def _on_runtime_changed(self, _event) -> None:
        self.refresh()

    def _build_widgets(self) -> list[dict[str, object]]:
        return [
            {
                "overlayId": record.overlay_id,
                "widgetId": record.widget_id,
                "widgetType": record.widget_type,
                "label": record.label,
                "source": record.source,
                "status": record.status.value,
                "connectorIds": list(record.connector_ids),
                "errorMessage": record.error_message,
            }
            for record in self._runtime.active_overlay_widget_records()
        ]

    def refresh(self) -> None:
        self._widgets = self._build_widgets()
        self.widgetsChanged.emit()

    def items(self) -> list[dict[str, object]]:
        return list(self._widgets)

    @Property(list, notify=widgetsChanged)
    def widgets(self) -> list[dict[str, object]]:
        return list(self._widgets)
