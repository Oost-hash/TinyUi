"""Connector read capability."""

from __future__ import annotations

from PySide6.QtCore import Property, QObject, Signal, Slot

from runtime.provider_registry import ProviderRegistry
from runtime_schema import EventBus, EventType, ProviderRegisteredData, ProviderUnregisteredData, ProviderUpdatedData


class ConnectorRead(QObject):
    """Expose connector-backed provider snapshots to QML consumers."""

    providersChanged = Signal()
    providerDataChanged = Signal(str)

    def __init__(self, event_bus: EventBus, providers: ProviderRegistry, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._event_bus = event_bus
        self._providers = providers
        self._provider_labels: dict[str, str] = {}
        self._provider_plugins: dict[str, str] = {}
        self._subscribe()

    def _subscribe(self) -> None:
        self._event_bus.on(EventType.PROVIDER_REGISTERED, self._on_provider_registered, replay_history=True)
        self._event_bus.on(EventType.PROVIDER_UNREGISTERED, self._on_provider_unregistered, replay_history=True)
        self._event_bus.on(EventType.PROVIDER_UPDATED, self._on_provider_updated)

    def _on_provider_registered(self, event) -> None:
        data = event.data
        if isinstance(data, ProviderRegisteredData):
            self._provider_labels[data.provider_id] = data.display_name or data.provider_id
            self._provider_plugins[data.provider_id] = data.plugin_id
            self.providersChanged.emit()
            self.providerDataChanged.emit(data.provider_id)

    def _on_provider_unregistered(self, event) -> None:
        data = event.data
        if isinstance(data, ProviderUnregisteredData):
            self._provider_labels.pop(data.provider_id, None)
            self._provider_plugins.pop(data.provider_id, None)
            self.providersChanged.emit()
            self.providerDataChanged.emit(data.provider_id)

    def _on_provider_updated(self, event) -> None:
        data = event.data
        if isinstance(data, ProviderUpdatedData):
            self.providerDataChanged.emit(data.provider_id)

    @Property(list, notify=providersChanged)
    def providers(self) -> list[dict]:
        return [
            {
                "id": provider_id,
                "label": self._provider_labels.get(provider_id, provider_id),
                "pluginId": self._provider_plugins.get(provider_id, ""),
            }
            for provider_id in self._providers.ids()
        ]

    @Slot(str, result=list)
    def inspectionRows(self, provider_id: str) -> list[dict]:
        return [{"key": key, "value": value} for key, value in self._providers.inspect(provider_id)]
