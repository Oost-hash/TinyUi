"""Plugin state read capability for lifecycle, errors, and history."""

from __future__ import annotations

from PySide6.QtCore import Property, QObject, Signal

from runtime.runtime import Runtime
from runtime_schema import Event, EventBus, EventType, PluginErrorData, PluginStateData


class PluginStateRead(QObject):
    """QML-facing plugin lifecycle state derived from runtime events."""

    pluginStateChanged = Signal(str, str)
    pluginError = Signal(str, str)
    stateDataChanged = Signal()

    def __init__(self, runtime: Runtime, event_bus: EventBus, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._runtime = runtime
        self._event_bus = event_bus
        self._states: dict[str, str] = {}
        self._errors: dict[str, str] = {}
        self._histories: dict[str, list[dict]] = {}
        self._rebuild()
        self._subscribe_to_events()

    def _subscribe_to_events(self) -> None:
        self._event_bus.on(EventType.PLUGIN_STATE_CHANGED, self._on_state_changed)
        self._event_bus.on(EventType.PLUGIN_ERROR, self._on_error)

    def _history_for(self, plugin_id: str) -> list[dict]:
        sm = self._runtime.get_plugin_state_machine(plugin_id)
        if sm is None:
            return []
        return [
            {
                "from": item.from_state.name.lower(),
                "to": item.to_state.name.lower(),
                "time": item.timestamp,
                "reason": item.reason,
            }
            for item in sm.history
        ]

    def _rebuild(self) -> None:
        states: dict[str, str] = {}
        errors: dict[str, str] = {}
        histories: dict[str, list[dict]] = {}
        for plugin_id in self._runtime.plugin_ids():
            sm = self._runtime.get_plugin_state_machine(plugin_id)
            if sm is None:
                continue
            states[plugin_id] = sm.state_name
            errors[plugin_id] = sm.error_message or ""
            histories[plugin_id] = self._history_for(plugin_id)
        self._states = states
        self._errors = errors
        self._histories = histories

    def _on_state_changed(self, event: Event[PluginStateData]) -> None:
        data = event.data
        self._states[data.plugin_id] = data.new_state
        self._histories[data.plugin_id] = self._history_for(data.plugin_id)
        sm = self._runtime.get_plugin_state_machine(data.plugin_id)
        self._errors[data.plugin_id] = "" if sm is None or sm.error_message is None else sm.error_message
        self.pluginStateChanged.emit(data.plugin_id, data.new_state)
        self.stateDataChanged.emit()

    def _on_error(self, event: Event) -> None:
        data = event.data
        if isinstance(data, PluginErrorData):
            self._errors[data.plugin_id] = data.error_message
            self._histories[data.plugin_id] = self._history_for(data.plugin_id)
            self.pluginError.emit(data.plugin_id, data.error_message)
            self.stateDataChanged.emit()

    @Property(dict, notify=stateDataChanged)
    def states(self) -> dict[str, str]:
        return dict(self._states)

    @Property(dict, notify=stateDataChanged)
    def errors(self) -> dict[str, str]:
        return dict(self._errors)

    @Property(dict, notify=stateDataChanged)
    def histories(self) -> dict[str, list[dict]]:
        return {key: list(value) for key, value in self._histories.items()}
