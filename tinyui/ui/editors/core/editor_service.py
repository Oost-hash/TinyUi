#
#  TinyUi - Editor Service Base
#  Copyright (C) 2026 Oost-hash
#

from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, Optional, TypeVar

from PySide2.QtCore import QObject, Signal

T = TypeVar("T")


class EditorService(QObject, Generic[T]):
    """
    Base Service - handles data fetching, transformation, and persistence.
    No UI code. Can be tested without Qt.
    """

    load_started = Signal()
    load_completed = Signal(object)  # loaded data
    load_failed = Signal(str)  # error message

    save_started = Signal()
    save_completed = Signal()
    save_failed = Signal(str)

    def __init__(self, store_adapter: Any, schema: Any = None):
        super().__init__()
        self._store = store_adapter
        self._schema = schema
        self._cache: Optional[Dict] = None

    @abstractmethod
    def load(self) -> Dict[str, T]:
        """
        Load raw data from store and transform to domain models.
        Returns dict of domain objects.
        """
        pass

    @abstractmethod
    def save(self, data: Dict[str, T]) -> bool:
        """
        Validate and persist data.
        Returns True on success.
        """
        pass

    @abstractmethod
    def validate(self, data: Dict[str, T]) -> tuple[bool, Optional[str]]:
        """
        Validate data before save.
        Returns (is_valid, error_message).
        """
        return True, None

    def transform_to_models(self, raw_data: Dict) -> Dict[str, T]:
        """
        Transform raw dict to domain objects.
        Override for type conversion.
        """
        # Default: pass through
        return raw_data

    def transform_from_models(self, models: Dict[str, T]) -> Dict:
        """
        Transform domain objects back to raw dict for persistence.
        Override for type conversion.
        """
        # Default: pass through
        return models

    def get_default(self) -> Dict[str, T]:
        """
        Get default/empty data.
        """
        return {}

    def clear_cache(self):
        """Clear internal cache."""
        self._cache = None
