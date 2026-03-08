#
#  TinyUi - Brake Editor View
#  Copyright (C) 2026 Oost-hash
#

from typing import List

from PySide2.QtWidgets import QComboBox

from ..components.base_editor_view import BaseEditorView
from .viewmodel import BrakeEditorVM


class BrakeEditorView(BaseEditorView[BrakeEditorVM]):
    """
    Brake editor view - now just handles brake-specific UI.
    Common structure inherited from BaseEditorView.
    """

    def __init__(self, parent=None):
        super().__init__(
            headers=["Brake Name", "Failure (mm)", "Heatmap"],
            column_widths={1: 100, 2: 150},
            parent=parent,
        )

    def _refresh_table(self):
        """Override: populate table with brake data."""
        if not self._vm or not self._vm.data:
            return

        # Standard text columns
        self._table.bind_data(
            self._vm.data.to_dict(), row_factory=self._vm.get_row_data
        )

        # Custom widget: heatmap dropdown
        for row, (key, item) in enumerate(self._vm.data.items()):
            self._add_heatmap_dropdown(row, 2, item.get("heatmap", "default"), key)

    def _add_heatmap_dropdown(self, row: int, col: int, current: str, key: str):
        """Add heatmap selector."""
        combo = QComboBox()
        combo.addItems(self._vm.heatmap_options)
        combo.setCurrentText(current)
        combo.currentTextChanged.connect(
            lambda text, k=key: self._vm.update_brake_field(k, "heatmap", text)
        )
        self._set_cell_widget(row, col, combo)

    def _on_add_clicked(self):
        """Override: add new brake."""
        if self._vm:
            self._vm.add_new_brake()
