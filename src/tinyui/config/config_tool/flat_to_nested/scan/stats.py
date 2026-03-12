"""Statistieken aggregatie per component/attribuut."""

from collections import Counter, defaultdict
from typing import Any, Dict, List, Tuple

from .keys import infer_type


def aggregate(key_values: Dict[str, List[Any]]) -> Dict[str, Dict]:
    """Bepaal per key: type, voorbeelden, modus."""
    result = {}

    for key, values in key_values.items():
        typ = infer_type(values)

        # Unieke representaties als voorbeelden (max 5)
        unique_examples = list(dict.fromkeys(repr(v) for v in values))[:5]

        # Meest voorkomende waarde (modus)
        str_values = [repr(v) for v in values]
        counter = Counter(str_values)
        mode = counter.most_common(1)[0][0] if counter else "None"

        result[key] = {"type": typ, "examples": unique_examples, "mode": mode}

    return result


def collect_by_component(
    key_values: Dict[str, List[Any]], matcher, configs: Dict[str, Dict]
) -> Tuple[Dict, Dict]:
    """Verzamel stats per component (prefix en numbered)."""

    # Prefix components: naam -> {suffixes, widgets, keys}
    prefix_components: Dict[str, Dict] = defaultdict(
        lambda: {"suffixes": set(), "widgets": set(), "keys": []}
    )

    # Numbered components: naam -> {indices, attributes, keys_per_index}
    numbered_components: Dict[str, Dict] = defaultdict(
        lambda: {
            "indices": set(),
            "attributes": set(),
            "keys_per_index": defaultdict(list),
        }
    )

    # Classificeer alle keys
    for key in key_values:
        match = matcher.match(key)
        if not match:
            continue

        if match.index is None:
            # Prefix component
            comp = prefix_components[match.component_name]
            comp["suffixes"].add(match.attribute)
            comp["keys"].append(key)
            # Bepaal in welke widgets deze key voorkomt
            for wname, cfg in configs.items():
                if key in cfg:
                    comp["widgets"].add(wname)
        else:
            # Numbered component
            comp = numbered_components[match.component_name]
            comp["indices"].add(match.index)
            comp["attributes"].add(match.attribute)
            # Hier was de bug: keys_per_index is een defaultdict(list)
            comp["keys_per_index"][match.index].append(key)

    # Verrijk met type info en stats
    prefix_result = {}
    for name, data in prefix_components.items():
        attr_info = {}
        for suffix in data["suffixes"]:
            full_key = f"{name}_{suffix}"
            if full_key in key_values:
                values = key_values[full_key]
                attr_info[suffix] = {
                    "type": infer_type(values),
                    "examples": list(dict.fromkeys(repr(v) for v in values))[:5],
                    "mode": Counter(repr(v) for v in values).most_common(1)[0][0]
                    if values
                    else "None",
                }

        prefix_result[name] = {
            "suffixes": sorted(data["suffixes"]),
            "widgets": sorted(data["widgets"]),
            "attributes": attr_info,
        }

    numbered_result = {}
    for name, data in numbered_components.items():
        attr_info = {}
        for attr in data["attributes"]:
            # Verzamel alle waarden voor dit attribuut over alle indices
            all_values = []
            for idx in data["indices"]:
                key = f"{name}_{idx}_{attr}"
                if key in key_values:
                    all_values.extend(key_values[key])

            attr_info[attr] = {
                "type": infer_type(all_values),
                "examples": list(dict.fromkeys(repr(v) for v in all_values))[:5],
                "mode": Counter(repr(v) for v in all_values).most_common(1)[0][0]
                if all_values
                else "None",
            }

        numbered_result[name] = {
            "indices": sorted(data["indices"]),
            "attributes": sorted(data["attributes"]),
            "attributes_info": attr_info,
        }

    return prefix_result, numbered_result
