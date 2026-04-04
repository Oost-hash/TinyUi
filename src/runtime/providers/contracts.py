"""Provider runtime contracts."""

from __future__ import annotations

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
