# editors/core/observable_model.py

import copy
from typing import Any, Dict, Optional

from PySide2.QtCore import QObject, Signal


class ObservableDict(QObject):
    """
    Dictionary with automatic change tracking and signals.
    Emits signals when data changes, enabling reactive UI updates.
    """

    data_changed = Signal(str, str, object)  # key, field, value
    item_added = Signal(str, object)  # key, item
    item_removed = Signal(str)  # key
    modified_changed = Signal(bool)  # is_modified

    def __init__(self, data: Optional[Dict] = None):
        super().__init__()
        self._data = data or {}
        self._original = {
            k: dict(v) if isinstance(v, dict) else v for k, v in self._data.items()
        }
        self._dirty = False

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def __setitem__(self, key: str, value: Any):
        old_value = self._data.get(key)
        if old_value != value:
            self._data[key] = value
            self._mark_dirty()
            self.data_changed.emit(key, "_value", value)

    def set_field(self, key: str, field: str, value: Any):
        """Set a field within a nested dict or object item."""
        if key not in self._data:
            self._data[key] = {}
        item = self._data[key]
        if isinstance(item, dict):
            old = item.get(field)
            if old != value:
                item[field] = value
                self._mark_dirty()
                self.data_changed.emit(key, field, value)
        else:
            old = getattr(item, field, None)
            if old != value:
                setattr(item, field, value)
                self._mark_dirty()
                self.data_changed.emit(key, field, value)

    def add_item(self, key: str, item: Any):
        """Add a new item to the collection."""
        self._data[key] = item
        self._mark_dirty()
        self.item_added.emit(key, item)

    def remove_item(self, key: str):
        """Remove an item from the collection."""
        if key in self._data:
            del self._data[key]
            self._mark_dirty()
            self.item_removed.emit(key)

    def _mark_dirty(self):
        if not self._dirty:
            self._dirty = True
            self.modified_changed.emit(True)

    def mark_clean(self):
        """Mark as clean (after save)."""
        self._dirty = False
        self._original = {
            k: dict(v) if isinstance(v, dict) else v for k, v in self._data.items()
        }
        self.modified_changed.emit(False)

    def is_modified(self) -> bool:
        return self._dirty

    def to_dict(self) -> Dict:
        """Export to plain dict for persistence."""
        return copy.deepcopy(self._data)

    def keys(self):
        return self._data.keys()

    def items(self):
        return self._data.items()

    def __contains__(self, key: str) -> bool:
        return key in self._data
