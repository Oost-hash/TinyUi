"""Scan tools - analyse en inspectie van flat configs."""

from .color_palettes import analyze_all_colors, analyze_widget_colors
from .columns import (
    analyze_all_cells,
    analyze_all_columns,
    analyze_widget_cells,
    analyze_widget_columns,
)
from .prefixes import (
    find_auto_prefixes,
    find_known_groups,
    find_reusable_groups,
    find_shared_suffixes,
    find_widget_groups,
)
from .suggest import format_dataclass, suggest_dataclasses

__all__ = [
    "analyze_all_cells",
    "analyze_all_columns",
    "analyze_widget_cells",
    "analyze_widget_columns",
    "analyze_all_colors",
    "analyze_widget_colors",
    "find_auto_prefixes",
    "find_known_groups",
    "find_reusable_groups",
    "find_shared_suffixes",
    "find_widget_groups",
    "format_dataclass",
    "suggest_dataclasses",
]
