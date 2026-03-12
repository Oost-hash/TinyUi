"""Key classificatie en type inference."""

from typing import Any, List


def is_column(key: str, column_patterns: List[str]) -> bool:
    """Check of een key een kolom attribuut is."""
    # Hardcoded kolom prefixes (kunnen later naar patterns.json)
    column_prefixes = (
        "column_index_",
        "show_",
        "font_color_",
        "bkg_color_",
        "decimal_places_",
        "prefix_",
        "suffix_",
        "low_",
        "high_",
        "warning_color_low_",
        "warning_color_high_",
        "number_of_",
    )

    # Check expliciete kolom prefixes
    if key.startswith(column_prefixes):
        # Uitzondering: show_ moet eindigen op warning_flash of geen _ hebben (dus geen show_position_x)
        if key.startswith("show_"):
            return key.endswith("_warning_flash") or key.count("_") == 1
        # low_ en high_ moeten eindigen op _threshold
        if key.startswith(("low_", "high_")):
            return key.endswith("_threshold")
        # number_of_ moet _warning_flashes bevatten
        if key.startswith("number_of_"):
            return "_warning_flashes" in key
        return True

    # Check suffix patterns (eindigt op _warning_flash_duration of _warning_flash_interval)
    if key.endswith(("_warning_flash_duration", "_warning_flash_interval")):
        return True

    return False


def infer_type(values: List[Any]) -> str:
    """Bepaal type annotation op basis van waarden."""
    types = set(type(v).__name__ for v in values if v is not None)

    if not types:
        return "Any"
    if "str" in types:
        return "str"
    if "bool" in types:
        return "bool"
    if "int" in types and "float" not in types:
        return "int"
    if "float" in types:
        return "float"
    return "Any"
