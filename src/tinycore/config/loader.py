"""JSON-based config loading and saving.

tinycore owns all config I/O. Plugins don't need custom loaders —
they provide default data and tinycore handles the rest.

Path layout: config_dir / plugin_name / filename.json
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .store import ConfigStore


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


class LoaderEntry:
    """Binds a config key to its file path and optional default data."""

    def __init__(self, key: str, path: Path, defaults: dict[str, Any] | None = None):
        self.key = key
        self.path = path
        self.defaults = defaults


class LoaderRegistry:
    """Maps config keys to their JSON file paths.

    Owns config_dir — the root directory for all plugin configs.
    Plugins register with (key, filename, plugin_name) and the
    registry resolves the full path as config_dir / plugin_name / filename.
    """

    def __init__(self, config_dir: Path | None = None):
        self._config_dir = config_dir
        self._entries: dict[str, LoaderEntry] = {}

    @property
    def config_dir(self) -> Path | None:
        return self._config_dir

    def register(
        self,
        key: str,
        filename: str,
        plugin_name: str,
        defaults: dict[str, Any] | None = None,
    ) -> None:
        """Register a config file.

        Args:
            key: String key for ConfigStore lookup.
            filename: Just the filename, e.g. "heatmaps.json".
            plugin_name: Plugin that owns this config.
            defaults: Default data to write if file doesn't exist.
        """
        if self._config_dir is None:
            raise RuntimeError("config_dir not set on LoaderRegistry")
        path = self._config_dir / plugin_name / filename
        self._entries[key] = LoaderEntry(key, path, defaults)

    def load_all(self, store: ConfigStore) -> None:
        """Load all registered configs from disk into the store."""
        for entry in self._entries.values():
            data = read_json(entry.path)
            if not data and entry.defaults:
                data = entry.defaults
                write_json(entry.path, data)
            store.update(entry.key, data)

    def load_one(self, store: ConfigStore, key: str) -> None:
        """Load a single config from disk into the store."""
        entry = self._entries[key]
        data = read_json(entry.path)
        if not data and entry.defaults:
            data = entry.defaults
            write_json(entry.path, data)
        store.update(key, data)

    def save(self, store: ConfigStore, key: str) -> None:
        """Save a config from the store to disk."""
        entry = self._entries[key]
        data = store.get(key)
        write_json(entry.path, data)

    @property
    def registered_keys(self) -> set[str]:
        return set(self._entries.keys())
