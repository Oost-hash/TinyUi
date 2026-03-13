"""Statistics aggregation per component/attribute."""

from collections import Counter
from typing import Any, Dict, List

from .columns import analyze_all_columns


def aggregate(key_values: Dict[str, List[Any]]) -> Dict[str, Dict]:
    """Determine per key: type, examples, mode."""
    result = {}

    for key, values in key_values.items():
        types = set(type(v).__name__ for v in values if v is not None)

        if not types:
            type_annotation = "Any"
        elif "str" in types:
            type_annotation = "str"
        elif "bool" in types:
            type_annotation = "bool"
        elif "int" in types and "float" not in types:
            type_annotation = "int"
        elif "float" in types:
            type_annotation = "float"
        else:
            type_annotation = "Any"

        unique_examples = list(dict.fromkeys(repr(v) for v in values))[:5]
        str_values = [repr(v) for v in values]
        counter = Counter(str_values)
        mode = counter.most_common(1)[0][0] if counter else "None"

        result[key] = {
            "type": type_annotation,
            "examples": unique_examples,
            "mode": mode,
        }

    return result


def collect_by_component(configs: Dict[str, Dict]) -> Dict[str, Dict]:
    """Collect statistics per component based on column grouping."""
    all_columns = analyze_all_columns(configs)

    components = {}

    for widget_name, columns in all_columns.items():
        for col in columns:
            component_id = col["id"]

            if component_id not in components:
                components[component_id] = {
                    "widgets": [],
                    "columns": [],
                    "attributes": set(),
                }

            components[component_id]["widgets"].append(widget_name)
            components[component_id]["columns"].append(col)

            # Collect all attribute keys for this column
            for key in col.keys():
                if key not in ("id", "show_key"):
                    components[component_id]["attributes"].add(key)

    # Convert sets to sorted lists for serialization
    for comp in components.values():
        comp["attributes"] = sorted(comp["attributes"])

    return components
