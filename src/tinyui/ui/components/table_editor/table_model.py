#  TinyUI - A mod for TinyPedal
#  Copyright (C) 2026 Oost-hash
#
#  This file is part of TinyUI.
#
#  TinyUI is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  TinyUI is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#  TinyUI builds on TinyPedal by s-victor (https://github.com/s-victor/TinyPedal),
#  licensed under GPLv3. TinyPedal is included as a submodule.

# tinyui/ui/components/table_model.py
from copy import deepcopy
from typing import Any, Callable, Dict, List, Optional, TypeVar

from .column_spec import ColumnSpec

T = TypeVar("T")


class TableModel:
    """
    Observable data container voor tabular data.

    Gebruikt ColumnSpec voor:
    - Validatie van waardes
    - Type conversie
    - Default waardes

    Emiteert changes naar listeners (ViewModels).
    """

    def __init__(self, columns: List[ColumnSpec], data: Optional[List[Dict]] = None):
        self._columns: Dict[str, ColumnSpec] = {col.name: col for col in columns}
        self._column_order: List[str] = [col.name for col in columns]
        self._data: List[Dict[str, Any]] = []
        self._listeners: List[Callable[[str, Any, Any], None]] = []

        if data:
            for row in data:
                self._data.append(self._validate_row(row))

    # ========== Observable Pattern ==========

    def subscribe(self, callback: Callable[[str, Any, Any], None]):
        """Callback(property_name, old_value, new_value)"""
        self._listeners.append(callback)

    def _notify(self, property_name: str, old_value: Any, new_value: Any):
        for listener in self._listeners:
            listener(property_name, old_value, new_value)

    # ========== CRUD Operaties ==========

    def add_row(self, row_data: Optional[Dict] = None) -> int:
        """Voeg nieuwe row toe, return index"""
        if row_data is None:
            row_data = {}

        # Vul defaults in
        for col_name, col_spec in self._columns.items():
            if col_name not in row_data or row_data[col_name] is None:
                row_data[col_name] = deepcopy(col_spec.default_value)

        validated = self._validate_row(row_data)
        index = len(self._data)
        self._data.append(validated)
        self._notify("data", None, validated)
        return index

    def insert_row(self, index: int, row_data: Optional[Dict] = None) -> bool:
        """Insert row op specifieke index"""
        if index < 0 or index > len(self._data):
            return False

        if row_data is None:
            row_data = {}
            for col_name, col_spec in self._columns.items():
                row_data[col_name] = deepcopy(col_spec.default_value)

        validated = self._validate_row(row_data)
        self._data.insert(index, validated)
        self._notify("data", None, validated)
        return True

    def update_cell(self, row: int, column: str, value: Any) -> bool:
        """Update enkele cell, met validatie"""
        if not (0 <= row < len(self._data)):
            return False

        if column not in self._columns:
            return False

        col_spec = self._columns[column]
        if not col_spec.editable:
            return False

        # Validatie
        if col_spec.validator and not col_spec.validator(value):
            return False

        old_value = self._data[row].get(column)
        self._data[row][column] = value
        self._notify(f"data[{row}][{column}]", old_value, value)
        return True

    def delete_row(self, index: int) -> bool:
        """Verwijder row op index"""
        if not (0 <= index < len(self._data)):
            return False

        old = self._data.pop(index)
        self._notify("data", old, None)
        return True

    def delete_rows(self, indices: List[int]) -> int:
        """Batch delete, return aantal verwijderd"""
        # Sorteer descending om index shifts te vermijden
        sorted_indices = sorted(set(indices), reverse=True)
        deleted = 0
        for idx in sorted_indices:
            if self.delete_row(idx):
                deleted += 1
        return deleted

    # ========== Query ==========

    def get_data(self) -> List[Dict[str, Any]]:
        """Return alle data (deep copy)"""
        return deepcopy(self._data)

    def get_row(self, index: int) -> Optional[Dict[str, Any]]:
        if not (0 <= index < len(self._data)):
            return None
        return deepcopy(self._data[index])

    def get_cell(self, row: int, column: str) -> Any:
        if not (0 <= row < len(self._data)):
            return None
        return self._data[row].get(column)

    def row_count(self) -> int:
        return len(self._data)

    def column_names(self) -> List[str]:
        return self._column_order.copy()

    def get_column_spec(self, name: str) -> Optional[ColumnSpec]:
        return self._columns.get(name)

    # ========== Sorting ==========

    def sort(self, column: str, ascending: bool = True):
        """Sorteer op kolom"""
        if column not in self._columns:
            return

        reverse = not ascending
        col_spec = self._columns[column]

        def sort_key(x: Dict[str, Any]):
            value = x.get(column)

            # None naar einde
            if value is None:
                return (1, 0)  # Tuple voor consistente vergelijking

            # Zorg dat type matcht met data_type voor consistente vergelijking
            try:
                if col_spec.data_type and not isinstance(value, col_spec.data_type):
                    value = col_spec.data_type(value)
            except (ValueError, TypeError):
                return (1, 0)  # Invalid value naar einde

            return (0, value)  # (is_valid, value) tuple

        self._data.sort(key=sort_key, reverse=reverse)
        self._notify("sort", None, (column, ascending))

    # ========== Batch Operaties ==========

    def apply_offset(
        self, column: str, indices: List[int], offset: float, scale: bool = False
    ):
        """Batch offset/scale voor numerieke kolommen"""
        if column not in self._columns:
            return

        col_spec = self._columns[column]
        if col_spec.data_type not in (int, float):
            return

        for idx in indices:
            if not (0 <= idx < len(self._data)):
                continue

            old_val = self._data[idx].get(column)
            if old_val is None:
                old_val = 0

            # Forceer numeriek type
            try:
                if col_spec.data_type is int:
                    old_val = int(old_val)
                else:
                    old_val = float(old_val)
            except (ValueError, TypeError):
                continue  # Skip non-numeric

            if scale:
                new_val = old_val * offset
            else:
                new_val = old_val + offset

            self.update_cell(idx, column, new_val)

    # ========== Private ==========

    def _validate_row(self, row_data: Dict) -> Dict[str, Any]:
        """Valideer en converteer row data volgens ColumnSpec"""
        result = {}

        for col_name, col_spec in self._columns.items():
            value = row_data.get(col_name)

            # Gebruik default als missing/None
            if value is None:
                value = deepcopy(col_spec.default_value)

            # Type conversie
            if value is not None and col_spec.data_type:
                try:
                    # Speciale afhandeling voor bool
                    if col_spec.data_type is bool:  # ← IS ipv ==
                        value = bool(value)
                    else:
                        value = col_spec.data_type(value)
                except (ValueError, TypeError):
                    value = deepcopy(col_spec.default_value)

            # Formatter + Parser ronde voor strings
            if isinstance(value, str) and col_spec.parser:
                try:
                    value = col_spec.parser(value)
                except (ValueError, TypeError):
                    pass

            result[col_name] = value

        return result
