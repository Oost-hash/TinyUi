"""Suggereer dataclasses op basis van gedeelde prefixes."""

from collections import defaultdict
from typing import Any, Dict, List

from ..utils import to_class_name
from .prefixes import find_reusable_groups


def suggest_dataclasses(
    configs: Dict[str, Dict],
    min_widgets: int = 2,
    min_attrs: int = 2,
) -> List[Dict]:
    """Suggereer dataclasses op basis van gedeelde suffixen."""
    candidates = find_reusable_groups(configs, min_widgets, min_attrs)

    by_widgets = defaultdict(list)
    for c in candidates:
        key = tuple(sorted(c["widgets"]))
        by_widgets[key].append(c)

    suggestions = []
    for widgets, members in sorted(by_widgets.items(), key=lambda x: -len(x[1])):
        class_base = _find_common_name(widgets, members)
        class_name = to_class_name(class_base) + "Config"

        fields = []
        for member in members:
            field = {
                "name": member["suffix"],
                "attrs": {},
            }
            for attr in member["attrs"]:
                field["attrs"][attr] = member["values"].get(attr)
            fields.append(field)

        suggestions.append({
            "class_name": class_name,
            "widgets": list(widgets),
            "widget_count": len(widgets),
            "fields": fields,
            "field_count": len(fields),
        })

    return suggestions


def _find_common_name(widgets: tuple, members: List[Dict]) -> str:
    """Vind een beschrijvende naam voor de dataclass."""
    widget_set = set(widgets)

    known = {
        frozenset({"relative", "rivals", "standings"}): "leaderboard",
        frozenset({"flag", "relative", "rivals", "standings"}): "flag_status",
        frozenset({"relative", "standings"}): "leaderboard_player",
        frozenset({"fuel", "virtual_energy"}): "energy",
        frozenset({"brake_wear", "tyre_wear"}): "wear",
        frozenset({"pace_notes", "track_notes"}): "notes",
        frozenset({"lap_time_history", "stint_history"}): "history",
        frozenset({"instrument", "trailing"}): "input",
        frozenset({"pedal", "trailing"}): "pedal_input",
        frozenset({"battery", "gear"}): "battery_gear",
    }

    for known_set, name in known.items():
        if widget_set == known_set:
            return name

    for known_set, name in known.items():
        if known_set.issubset(widget_set):
            return name

    if len(widgets) == 2:
        parts_a = set(widgets[0].split("_"))
        parts_b = set(widgets[1].split("_"))
        common = parts_a & parts_b
        if common:
            return "_".join(sorted(common))

    return "_".join(w.split("_")[0] for w in widgets[:2])


def format_dataclass(suggestion: Dict) -> str:
    """Genereer een dataclass preview als string."""
    lines = []
    lines.append("@dataclass")
    lines.append(f"class {suggestion['class_name']}:")
    lines.append(f'    """Shared by: {", ".join(suggestion["widgets"])}"""')
    lines.append("")

    for field in suggestion["fields"]:
        attrs = field["attrs"]
        if len(attrs) == 1:
            attr, value = next(iter(attrs.items()))
            type_hint = _type_hint(value)
            lines.append(f"    {field['name']}: {type_hint} = {repr(value)}")
        else:
            lines.append(f"    # {field['name']}")
            for attr, value in sorted(attrs.items()):
                type_hint = _type_hint(value)
                lines.append(
                    f"    {field['name']}_{attr}: {type_hint} = {repr(value)}"
                )
    lines.append("")
    return "\n".join(lines)


def _type_hint(value: Any) -> str:
    """Bepaal type hint op basis van waarde."""
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, int):
        return "int"
    if isinstance(value, float):
        return "float"
    if isinstance(value, str):
        return "str"
    return "Any"
