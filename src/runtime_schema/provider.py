"""Provider lifecycle event schemas."""

from __future__ import annotations

from dataclasses import dataclass


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
