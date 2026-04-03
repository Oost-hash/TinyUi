"""Plugin state capability for lifecycle and error projection."""

from __future__ import annotations

from PySide6.QtCore import Property, QObject, Signal

from runtime_schema import Event, EventBus, EventType, PluginErrorData, PluginStateData


class PluginStateReadModel(QObject):
    """QML-facing plugin lifecycle and error state derived from runtime events."""

    pluginStateChanged = Signal(str, str)
    pluginError = Signal(str, str)
    statesChanged = Signal()

    def __init__(self, event_bus: EventBus, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._event_bus = event_bus
        self._states: dict[str, str] = {}
        self._errors: dict[str, str] = {}
        self._subscribe_to_events()

    def _subscribe_to_events(self) -> None:
        self._event_bus.on(EventType.PLUGIN_STATE_CHANGED, self._on_state_changed)
        self._event_bus.on(EventType.PLUGIN_ERROR, self._on_error)

    def _on_state_changed(self, event: Event[PluginStateData]) -> None:
        data = event.data
        self._states[data.plugin_id] = data.new_state
        self.pluginStateChanged.emit(data.plugin_id, data.new_state)
        self.statesChanged.emit()

    def _on_error(self, event: Event) -> None:
        data = event.data
        if isinstance(data, PluginErrorData):
            self._errors[data.plugin_id] = data.error_message
            self.pluginError.emit(data.plugin_id, data.error_message)
            self.statesChanged.emit()

    @Property(dict, notify=statesChanged)
    def states(self) -> dict[str, str]:
        """Current lifecycle state per plugin."""
        return dict(self._states)

    @Property(dict, notify=statesChanged)
    def errors(self) -> dict[str, str]:
        """Current error message per plugin."""
        return dict(self._errors)
