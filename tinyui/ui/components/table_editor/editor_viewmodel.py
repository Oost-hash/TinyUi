# tinyui/ui/components/editor_viewmodel.py
from typing import Any, Callable, List, Optional

from PySide2.QtCore import QObject, Signal

from .table_model import TableModel


class EditorViewModel(QObject):
    """
    ViewModel voor editor dialogs.

    Verbindt TableModel met UI via signals.
    Handelt modified tracking, save/revert af.
    """

    # Signals voor UI updates
    data_changed = Signal()  # Data gewijzigd (refresh table)
    modified_changed = Signal(bool)  # Modified flag changed
    error_occurred = Signal(str)  # Error message
    saved = Signal()  # Succesvol opgeslagen

    def __init__(
        self,
        model: TableModel,
        saver: Callable[[List[dict]], bool],
        validator: Optional[Callable[[List[dict]], Optional[str]]] = None,
    ):
        super().__init__()
        self._model = model
        self._saver = saver
        self._validator = validator

        # Track originele state voor modified detection
        self._original_data = model.get_data()

        # Subscribe naar model changes
        self._model.subscribe(self._on_model_change)

    # ========== Properties ==========

    @property
    def model(self) -> TableModel:
        return self._model

    def is_modified(self) -> bool:
        """Vergelijk huidige data met originele data"""
        return self._model.get_data() != self._original_data

    # ========== CRUD Delegatie ==========

    def add_row(self, row_data: Optional[dict] = None) -> int:
        return self._model.add_row(row_data)

    def insert_row(self, index: int, row_data: Optional[dict] = None) -> bool:
        return self._model.insert_row(index, row_data)

    def update_cell(self, row: int, column: str, value: Any) -> bool:
        return self._model.update_cell(row, column, value)

    def delete_rows(self, indices: List[int]) -> int:
        return self._model.delete_rows(indices)

    def sort(self, column: str, ascending: bool = True):
        self._model.sort(column, ascending)

    def apply_offset(
        self, column: str, indices: List[int], offset: float, scale: bool = False
    ):
        self._model.apply_offset(column, indices, offset, scale)

    # ========== Save / Revert ==========

    def save(self) -> bool:
        """Save data via saver callback"""
        data = self._model.get_data()

        # Pre-save validatie
        if self._validator:
            error = self._validator(data)
            if error:
                self.error_occurred.emit(error)
                return False

        # Save
        try:
            success = self._saver(data)
            if success:
                self._original_data = data  # Reset baseline
                self.modified_changed.emit(False)
                self.saved.emit()
            return success
        except Exception as e:
            self.error_occurred.emit(f"Save failed: {str(e)}")
            return False

    def revert(self):
        """Revert naar originele data"""
        # Herstel originele data
        # (In echte implementatie: reload from source of maak nieuw model)
        self._model._data = [row.copy() for row in self._original_data]
        self._model._notify("revert", None, None)
        self.modified_changed.emit(False)

    def confirm_discard(self) -> str:
        """
        Return status voor discard check:
        'proceed' - geen changes
        'save' - user wil eerst saven
        'discard' - user gooit weg
        'cancel' - user annuleert
        """
        if not self.is_modified():
            return "proceed"
        return "ask_user"  # UI toont dialog

    # ========== Private ==========

    def _on_model_change(self, property_name: str, old_val: Any, new_val: Any):
        """Callback van model"""
        self.data_changed.emit()
        self.modified_changed.emit(self.is_modified())
