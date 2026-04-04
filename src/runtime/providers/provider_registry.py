"""Runtime registry for connector-backed providers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from runtime.providers.contracts import InspectionSnapshot, ProviderAccess


def _empty_snapshot() -> InspectionSnapshot:
    return []


@dataclass
class RegisteredProvider:
    """Provider instance and metadata."""

    provider_id: str
    plugin_id: str
    display_name: str
    instance: Any


class ProviderRegistry(ProviderAccess):
    """Stores active providers and exposes common control operations."""

    def __init__(self) -> None:
        self._providers: dict[str, RegisteredProvider] = {}

    def register(self, provider_id: str, plugin_id: str, display_name: str, instance: Any) -> None:
        self._providers[provider_id] = RegisteredProvider(
            provider_id=provider_id,
            plugin_id=plugin_id,
            display_name=display_name,
            instance=instance,
        )

    def unregister(self, provider_id: str) -> bool:
        return self._providers.pop(provider_id, None) is not None

    def has(self, provider_id: str) -> bool:
        return provider_id in self._providers

    def get(self, provider_id: str) -> Any | None:
        provider = self._providers.get(provider_id)
        return provider.instance if provider else None

    def metadata(self, provider_id: str) -> RegisteredProvider | None:
        return self._providers.get(provider_id)

    def ids(self) -> list[str]:
        return list(self._providers.keys())

    def inspect(self, provider_id: str) -> InspectionSnapshot:
        provider = self.get(provider_id)
        if provider is None or not hasattr(provider, "inspect_snapshot"):
            return _empty_snapshot()
        snapshot = provider.inspect_snapshot()
        return list(snapshot) if isinstance(snapshot, list) else _empty_snapshot()

    def request_source(self, provider_id: str, owner: str, source_name: str) -> bool:
        provider = self.get(provider_id)
        if provider is None or not hasattr(provider, "request_source"):
            return False
        return bool(provider.request_source(owner, source_name))

    def release_source(self, provider_id: str, owner: str) -> bool:
        provider = self.get(provider_id)
        if provider is None or not hasattr(provider, "release_source"):
            return False
        return bool(provider.release_source(owner))

    def update(self, provider_id: str) -> bool:
        provider = self.get(provider_id)
        if provider is None or not hasattr(provider, "update"):
            return False
        provider.update()
        return True
