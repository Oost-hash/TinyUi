"""ProviderRegistry — type-keyed provider lookup."""

from __future__ import annotations

from typing import TypeVar

from .protocol import Provider

T = TypeVar("T")


class ProviderRegistry:
    """Type-keyed registry for pull-based providers."""

    def __init__(self):
        self._providers: dict[type, Provider] = {}

    def register(self, data_type: type[T], provider: Provider[T]) -> None:
        """Register a provider for a data type."""
        self._providers[data_type] = provider

    def get(self, data_type: type[T]) -> T:
        """Pull current value from the provider. Raises KeyError if not registered."""
        if data_type not in self._providers:
            raise KeyError(f"No provider registered for {data_type}")
        return self._providers[data_type].get()

    def has(self, data_type: type) -> bool:
        """Check if a provider is registered for this type."""
        return data_type in self._providers
