#
#  TinyUi - Store Adapters
#  Copyright (C) 2026 Oost-hash
#

from abc import ABC, abstractmethod
from typing import Any, Dict, Protocol


class IStoreAdapter(Protocol):
    """Protocol for store adapters - enables swapping implementations."""

    def load(self, cfg_attr: str) -> Dict:
        """Load configuration by attribute name."""
        ...

    def save(self, cfg_attr: str, cfg_type: Any, data: Dict) -> bool:
        """Save configuration."""
        ...

    def load_default(self, cfg_attr: str) -> Dict:
        """Load default configuration."""
        ...


class ConfigStoreAdapter:
    """
    Adapter for cfg.user store (your current _store module).
    Bridges old imperative API to new interface.
    """

    def __init__(self, store_module: Any = None):
        # Lazy import to avoid circular dependencies
        if store_module is None:
            from .. import _store as store_module
        self._store = store_module

    def load(self, cfg_attr: str) -> Dict:
        return self._store.load(cfg_attr)

    def save(self, cfg_attr: str, cfg_type: Any, data: Dict) -> bool:
        try:
            self._store.save(cfg_attr, cfg_type, data)
            return True
        except Exception:
            return False

    def load_default(self, cfg_attr: str) -> Dict:
        return self._store.load_default(cfg_attr)


class MockStoreAdapter:
    """
    In-memory store for testing.
    No file I/O, no Qt, no external dependencies.
    """

    def __init__(self, initial_data: Dict[str, Dict] = None):
        self._data = initial_data or {}
        self._defaults: Dict[str, Dict] = {}

    def load(self, cfg_attr: str) -> Dict:
        return dict(self._data.get(cfg_attr, {}))

    def save(self, cfg_attr: str, cfg_type: Any, data: Dict) -> bool:
        self._data[cfg_attr] = dict(data)
        return True

    def load_default(self, cfg_attr: str) -> Dict:
        return dict(self._defaults.get(cfg_attr, {}))

    def set_default(self, cfg_attr: str, data: Dict):
        """Set default data for testing."""
        self._defaults[cfg_attr] = dict(data)
