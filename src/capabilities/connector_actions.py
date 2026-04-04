"""Connector actions capability."""

from __future__ import annotations

from PySide6.QtCore import QObject, Signal, Slot

from runtime.provider_registry import ProviderRegistry


class ConnectorActions(QObject):
    """Expose provider-side operational actions to QML consumers."""

    providerDataChanged = Signal(str)

    def __init__(self, providers: ProviderRegistry, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._providers = providers

    @Slot(str, str, str, result=bool)
    def requestSource(self, provider_id: str, owner: str, source_name: str) -> bool:
        result = self._providers.request_source(provider_id, owner, source_name)
        if result:
            self.providerDataChanged.emit(provider_id)
        return result

    @Slot(str, str, result=bool)
    def releaseSource(self, provider_id: str, owner: str) -> bool:
        result = self._providers.release_source(provider_id, owner)
        if result:
            self.providerDataChanged.emit(provider_id)
        return result

    @Slot(str, result=bool)
    def updateProvider(self, provider_id: str) -> bool:
        result = self._providers.update(provider_id)
        if result:
            self.providerDataChanged.emit(provider_id)
        return result
