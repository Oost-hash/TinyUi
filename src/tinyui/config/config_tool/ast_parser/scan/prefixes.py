"""Prefix/suffix detectie voor herbruikbare dataclasses."""

from collections import defaultdict
from typing import Any, Dict, List, Set, Tuple

from ..model import BAR, BASE, CELL_PREFIXES, FONT, KNOWN_GROUPS, POSITION


def extract_suffixes(config: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Extraheer suffixen en hun attributen uit een widget config."""
    result = defaultdict(dict)

    for key, value in config.items():
        for prefix in CELL_PREFIXES:
            if key.startswith(prefix):
                suffix = key[len(prefix):]
                attr = prefix.rstrip("_")
                result[suffix][attr] = value
                break

    return dict(result)


def find_auto_prefixes(
    configs: Dict[str, Dict],
    min_widgets: int = 2,
    min_fields: int = 3,
) -> Dict[str, Dict]:
    """Detecteer automatisch prefix-groepen over alle widgets."""
    claimed_keys = set()
    for group_keys in KNOWN_GROUPS.values():
        claimed_keys.update(group_keys)

    def is_claimed(key):
        if key in claimed_keys:
            return True
        for prefix in CELL_PREFIXES:
            if key.startswith(prefix):
                return True
        return False

    prefix_data = defaultdict(lambda: defaultdict(dict))

    for wname, config in configs.items():
        unclaimed = {k: v for k, v in config.items() if not is_claimed(k)}
        widget_prefixes = _find_key_prefixes(unclaimed)

        for prefix, fields in widget_prefixes.items():
            if len(fields) >= min_fields:
                prefix_data[prefix][wname] = fields

    result = {}
    for prefix, widget_fields in prefix_data.items():
        if len(widget_fields) < min_widgets:
            continue

        all_field_names = set()
        for fields in widget_fields.values():
            all_field_names.update(fields.keys())

        common_fields = set(list(widget_fields.values())[0].keys())
        for fields in widget_fields.values():
            common_fields &= set(fields.keys())

        identical_fields = {}
        for field in common_fields:
            values = set(repr(widget_fields[w][field]) for w in widget_fields)
            if len(values) == 1:
                first_widget = list(widget_fields.keys())[0]
                identical_fields[field] = widget_fields[first_widget][field]

        result[prefix] = {
            "widgets": sorted(widget_fields.keys()),
            "widget_count": len(widget_fields),
            "all_fields": sorted(all_field_names),
            "common_fields": sorted(common_fields),
            "identical_fields": identical_fields,
            "field_count": len(all_field_names),
        }

    return result


def _find_key_prefixes(keys_dict: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Groepeer keys op langste gemeenschappelijk prefix binnen één widget."""
    prefix_groups = defaultdict(dict)

    for key, value in keys_dict.items():
        parts = key.split("_")
        for i in range(len(parts) - 1, 0, -1):
            prefix = "_".join(parts[:i])
            suffix = "_".join(parts[i:])
            prefix_groups[prefix][suffix] = value

    valid = {}
    for prefix, fields in sorted(prefix_groups.items(), key=lambda x: -len(x[0])):
        if len(fields) < 2:
            continue

        already_covered = False
        for existing in valid:
            if existing.startswith(prefix + "_"):
                already_covered = True
                break

        if not already_covered:
            valid[prefix] = fields

    return valid


def find_known_groups(configs: Dict[str, Dict]) -> Dict[str, Dict]:
    """Analyseer bekende groepen (font, position, base) over alle widgets."""
    group_defaults = {
        "font": ("FontConfig", FONT),
        "position": ("PositionConfig", POSITION),
        "bar": ("BarConfig", BAR),
        "base": ("WidgetBase", BASE),
    }

    result = {}

    for group_name, group_keys in KNOWN_GROUPS.items():
        class_name, _ = group_defaults[group_name]
        widgets_data = {}

        for wname, config in configs.items():
            found = {key: config[key] for key in group_keys if key in config}
            if found:
                widgets_data[wname] = found

        if not widgets_data:
            continue

        all_vals = list(widgets_data.values())
        common_keys = set(all_vals[0].keys())
        for v in all_vals[1:]:
            common_keys &= set(v.keys())

        identical = {}
        varying = {}
        for key in common_keys:
            values = set(repr(widgets_data[w][key]) for w in widgets_data)
            if len(values) == 1:
                identical[key] = all_vals[0][key]
            else:
                varying[key] = {
                    w: widgets_data[w][key] for w in widgets_data if key in widgets_data[w]
                }

        result[group_name] = {
            "class_name": class_name,
            "widget_count": len(widgets_data),
            "identical": identical,
            "varying": varying,
        }

    return result


def find_shared_suffixes(
    configs: Dict[str, Dict],
    min_widgets: int = 2,
) -> Dict[str, Dict]:
    """Vind suffixen die in meerdere widgets voorkomen."""
    suffix_data = defaultdict(lambda: defaultdict(dict))

    for wname, config in configs.items():
        widget_suffixes = extract_suffixes(config)
        for suffix, attrs in widget_suffixes.items():
            suffix_data[suffix][wname] = attrs

    result = {}
    for suffix, widget_vals in suffix_data.items():
        if len(widget_vals) < min_widgets:
            continue

        widgets = sorted(widget_vals.keys())

        attrs_info = defaultdict(lambda: defaultdict(list))
        for wname, attrs in widget_vals.items():
            for attr, value in attrs.items():
                attrs_info[attr][repr(value)].append(wname)

        vals_list = list(widget_vals.values())
        common_attrs = set(vals_list[0].keys())
        for v in vals_list[1:]:
            common_attrs &= set(v.keys())

        identical = bool(common_attrs)
        for attr in common_attrs:
            values = set(repr(widget_vals[w][attr]) for w in widget_vals)
            if len(values) > 1:
                identical = False
                break

        result[suffix] = {
            "widgets": widgets,
            "widget_count": len(widgets),
            "attrs": {
                attr: {
                    "values": {v: ws for v, ws in val_widgets.items()},
                    "identical": len(val_widgets) == 1,
                }
                for attr, val_widgets in attrs_info.items()
            },
            "common_attrs": sorted(common_attrs),
            "identical": identical,
        }

    return result


def find_reusable_groups(
    configs: Dict[str, Dict],
    min_widgets: int = 2,
    min_attrs: int = 2,
) -> List[Dict]:
    """Vind groepen van suffixen die herbruikbare dataclasses kunnen worden."""
    shared = find_shared_suffixes(configs, min_widgets)

    candidates = []
    for suffix, info in shared.items():
        if not info["identical"]:
            continue
        if len(info["common_attrs"]) < min_attrs:
            continue

        first_widget = info["widgets"][0]
        suffix_data = extract_suffixes(configs[first_widget])
        values = suffix_data.get(suffix, {})

        candidates.append({
            "suffix": suffix,
            "widget_count": info["widget_count"],
            "widgets": info["widgets"],
            "attrs": info["common_attrs"],
            "values": values,
        })

    return sorted(candidates, key=lambda c: -c["widget_count"])


def find_widget_groups(configs: Dict[str, Dict], min_shared: int = 3) -> List[Dict]:
    """Vind groepen widgets die veel suffixen delen."""
    shared = find_shared_suffixes(configs, min_widgets=2)

    pair_counts = defaultdict(lambda: {"shared": [], "identical": []})

    for suffix, info in shared.items():
        widgets = info["widgets"]
        for i, w1 in enumerate(widgets):
            for w2 in widgets[i + 1:]:
                pair = tuple(sorted([w1, w2]))
                pair_counts[pair]["shared"].append(suffix)
                if info["identical"]:
                    pair_counts[pair]["identical"].append(suffix)

    groups = []
    for (w1, w2), data in pair_counts.items():
        if len(data["identical"]) >= min_shared:
            groups.append({
                "widgets": [w1, w2],
                "shared_count": len(data["shared"]),
                "identical_count": len(data["identical"]),
                "identical_suffixes": sorted(data["identical"]),
            })

    return sorted(groups, key=lambda g: -g["identical_count"])
