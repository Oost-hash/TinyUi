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

# tinyui/ui/components/column_spec.py
from dataclasses import dataclass
from typing import Any, Callable, Optional


@dataclass
class ColumnSpec:
    """
    DSL: Definieer hoe één kolom in een tabel eruit ziet en werkt.

    Gebruik:
        ColumnSpec("temperature", float, editable=True, widget="spinbox")
        ColumnSpec("color", str, editable=True, widget="color_picker")
    """

    name: str  # Kolom naam
    data_type: type  # int, float, str, bool
    editable: bool = True  # Kan user editen?
    width: int = 0  # 0 = auto, anders pixels

    # Widget type voor editing
    widget: str = "default"  # "default", "spinbox", "color_picker",
    # "combo", "checkbox", "line_edit"

    # Validatie
    validator: Optional[Callable[[Any], bool]] = None

    # Formatting: hoe tonen we de waarde?
    formatter: Optional[Callable[[Any], str]] = None

    # Parsing: hoe converteren we string terug naar waarde?
    parser: Optional[Callable[[str], Any]] = None

    # Voor combo boxes: opties
    combo_options: Optional[list] = None

    # Standaard waarde voor nieuwe rijen
    default_value: Any = None


# Pre-built validators voor common cases
class Validators:
    @staticmethod
    def hex_color(value: str) -> bool:
        if not isinstance(value, str):
            return False
        return value.startswith("#") and len(value) in (4, 7, 9)

    @staticmethod
    def non_empty(value: str) -> bool:
        return bool(value and str(value).strip())

    @staticmethod
    def positive_float(value: float) -> bool:
        return isinstance(value, (int, float)) and value >= 0


# Pre-built formatters
class Formatters:
    @staticmethod
    def one_decimal(value: float) -> str:
        return f"{value:.1f}"

    @staticmethod
    def two_decimals(value: float) -> str:
        return f"{value:.2f}"

    @staticmethod
    def uppercase(value: str) -> str:
        return str(value).upper()


# Pre-built parsers
class Parsers:
    @staticmethod
    def float_or_zero(value: str) -> float:
        try:
            return float(value)
        except (ValueError, TypeError):
            return 0.0
