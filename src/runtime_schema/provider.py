"""Provider schema and access contracts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


InspectionSnapshot = list[tuple[str, str]]


class ProviderAccess(Protocol):
    """Read-only and control access to registered providers."""

    def has(self, provider_id: str) -> bool:
        """Return True when the provider is registered."""
        ...

    def get(self, provider_id: str) -> Any | None:
        """Return the raw provider instance when available."""
        ...

    def inspect(self, provider_id: str) -> InspectionSnapshot:
        """Return a snapshot for diagnostics and UI rendering."""
        ...

    def request_source(self, provider_id: str, owner: str, source_name: str) -> bool:
        """Request a specific source for a provider."""
        ...

    def release_source(self, provider_id: str, owner: str) -> bool:
        """Release a previous source request for a provider."""
        ...

    def update(self, provider_id: str) -> bool:
        """Advance the provider once when supported."""
        ...


@dataclass(frozen=True)
class ProviderRegisteredData:
    """Data for provider registration events."""

    provider_id: str
    plugin_id: str
    display_name: str = ""
    source: str = "connector"


@dataclass(frozen=True)
class ProviderUnregisteredData:
    """Data for provider removal events."""

    provider_id: str
    plugin_id: str


@dataclass(frozen=True)
class ProviderUpdatedData:
    """Data for provider snapshot/source updates."""

    provider_id: str
    plugin_id: str
