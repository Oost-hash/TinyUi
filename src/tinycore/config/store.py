"""ConfigStore — type-keyed config distribution.

A message broker for configuration, not a config manager.
The store has no domain knowledge. It stores typed snapshots
and notifies observers on changes.
"""

from __future__ import annotations

from typing import Any, Callable, TypeVar

T = TypeVar("T")


class ConfigStore:
    """Generic typed config store with push notifications."""

    def __init__(self):
        self._current: dict[type, Any] = {}
        self._observers: dict[type, list[Callable]] = {}

    def get(self, config_type: type[T]) -> T:
        """Get current snapshot for a config type.

        Raises KeyError if the type was never registered.
        """
        return self._current[config_type]

    def get_or_default(self, config_type: type[T], default: T) -> T:
        """Get current snapshot, or return default if not registered."""
        return self._current.get(config_type, default)

    def has(self, config_type: type) -> bool:
        """Check if a config type is registered."""
        return config_type in self._current

    def update(self, config_type: type[T], value: T) -> None:
        """Publish a new value. Notifies all observers of this type."""
        self._current[config_type] = value
        for callback in self._observers.get(config_type, []):
            callback(value)

    def observe(self, config_type: type[T], callback: Callable[[T], None]) -> Callable:
        """Subscribe to changes for a config type.

        Returns an unsubscribe function.
        """
        self._observers.setdefault(config_type, []).append(callback)

        def unsubscribe():
            self._observers[config_type].remove(callback)

        return unsubscribe

    @property
    def registered_types(self) -> set[type]:
        """All currently registered config types."""
        return set(self._current.keys())
