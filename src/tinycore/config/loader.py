"""ConfigLoader protocol + LoaderRegistry.

Loaders know how to read/write one config type from/to disk.
The registry maps config types to their loader + file path.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Protocol, TypeVar, runtime_checkable

from .store import ConfigStore

T = TypeVar("T")


@runtime_checkable
class ConfigLoader(Protocol[T]):
    """Knows how to load/save one config type."""

    def load(self, path: Path) -> T: ...
    def save(self, path: Path, config: T) -> None: ...


class LoaderEntry:
    """Binds a config type to its loader and file path."""

    def __init__(self, config_type: type, loader: ConfigLoader, path: Path):
        self.config_type = config_type
        self.loader = loader
        self.path = path


class LoaderRegistry:
    """Maps config types to their loader + file path.

    Orchestrates loading from disk into the store,
    and saving from the store back to disk.
    """

    def __init__(self):
        self._entries: dict[type, LoaderEntry] = {}

    def register(self, config_type: type[T], loader: ConfigLoader[T], path: Path) -> None:
        """Register a loader for a config type."""
        self._entries[config_type] = LoaderEntry(config_type, loader, path)

    def load_all(self, store: ConfigStore) -> None:
        """Load all registered config types from disk into the store."""
        for entry in self._entries.values():
            config = entry.loader.load(entry.path)
            store.update(entry.config_type, config)

    def load_one(self, store: ConfigStore, config_type: type[T]) -> None:
        """Load a single config type from disk into the store."""
        entry = self._entries[config_type]
        config = entry.loader.load(entry.path)
        store.update(config_type, config)

    def save(self, store: ConfigStore, config_type: type[T]) -> None:
        """Save a config type from the store to disk."""
        entry = self._entries[config_type]
        config = store.get(config_type)
        entry.loader.save(entry.path, config)

    @property
    def registered_types(self) -> set[type]:
        return set(self._entries.keys())


# --- Utility for JSON-based loaders ---


def read_json(path: Path) -> dict[str, Any]:
    """Read a JSON file, return empty dict if missing."""
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, data: dict[str, Any]) -> None:
    """Write a JSON file with consistent formatting."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
        f.write("\n")
