#
#  TinyUi - Base ViewModel
#  Copyright (C) 2025 Oost-hash
#

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Generic, Optional, TypeVar

from PySide2.QtCore import QObject, Signal

from .observable_model import ObservableDict

T = TypeVar("T")


class BaseViewModel(QObject, Generic[T]):
    """
    Base ViewModel - mediates between View and Service.
    Holds UI state, exposes data for binding, handles user actions.
    No Qt UI code except signals.
    """

    data_changed = Signal()  # Generic data refresh needed
    modified_changed = Signal(bool)  # Dirty state changed
    error_occurred = Signal(str)  # Error message for UI
    operation_completed = Signal(str)  # Success message

    def __init__(self, service: Any):
        super().__init__()
        self._service = service
        self._model: Optional[ObservableDict] = None
        self._is_loading = False

    @property
    def is_modified(self) -> bool:
        """Proxy to model's dirty state."""
        return self._model.is_modified() if self._model else False

    @property
    def data(self) -> Optional[ObservableDict]:
        """Access to underlying model."""
        return self._model

    def load(self) -> bool:
        """
        Load data from service.
        Returns True on success, False on error.
        """
        self._is_loading = True
        try:
            raw_data = self._service.load()
            self._model = ObservableDict(raw_data)

            # Proxy signals from model
            self._model.modified_changed.connect(self.modified_changed)
            self._model.data_changed.connect(self._on_data_changed)

            self.data_changed.emit()
            return True

        except Exception as e:
            self.error_occurred.emit(f"Failed to load: {str(e)}")
            return False
        finally:
            self._is_loading = False

    def save(self) -> bool:
        """
        Save data via service.
        Returns True on success, False on error.
        """
        if not self._model or not self.is_modified:
            return True  # Nothing to save

        try:
            # Validate before saving
            if not self._validate():
                return False

            # Persist
            success = self._service.save(self._model.to_dict())

            if success:
                self._model.mark_clean()
                self.operation_completed.emit("Saved successfully")
                return True
            else:
                self.error_occurred.emit("Save failed")
                return False

        except Exception as e:
            self.error_occurred.emit(f"Save error: {str(e)}")
            return False

    def update_value(self, key: str, field: str, value: Any):
        """
        Update a single value in the model.
        View calls this when user edits a cell.
        """
        if self._model:
            self._model.set_field(key, field, value)

    def add_item(self, key: str, item: Any):
        """Add new item to collection."""
        if self._model:
            self._model.add_item(key, item)

    def remove_item(self, key: str):
        """Remove item from collection."""
        if self._model:
            self._model.remove_item(key)

    def _on_data_changed(self, key: str, field: str, value: Any):
        """Handle model data changes - notify view."""
        # Override in subclass for specific field handling
        pass

    @abstractmethod
    def _validate(self) -> bool:
        """
        Validate data before save.
        Override in concrete VM.
        """
        return True

    @abstractmethod
    def get_row_data(self, key: str, item: Any) -> list:
        """
        Convert item to table row format.
        Override in concrete VM.
        """
        pass
