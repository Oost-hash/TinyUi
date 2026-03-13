"""Bereidt widget data voor templates."""

import keyword
import re
from typing import Any, Dict, List, Set

from ..scan.prefixes import KNOWN_GROUPS, KNOWN_PREFIXES


def _safe_id(name: str) -> str:
    """Maak Python-safe identifier."""
    safe = re.sub(r"[^a-zA-Z0-9_]", "_", name)
    if safe and safe[0].isdigit():
        safe = "_" + safe
    if keyword.iskeyword(safe):
        safe += "_"
    return safe


def _class_name(name: str) -> str:
    """Snake_case naar PascalCase."""
    return "".join(x.capitalize() for x in name.split("_"))


def _infer_type(value: Any) -> str:
    """Type hint voor waarde."""
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, int):
        return "int"
    if isinstance(value, float):
        return "float"
    if isinstance(value, str):
        return "str"
    return "Any"


def extract_base_keys(config: Dict[str, Any]) -> Dict[str, Any]:
    """Pop WidgetBase keys (enable, update_interval, opacity)."""
    base = {}
    for key in KNOWN_GROUPS["base"]["keys"]:
        if key in config:
            base[key] = config.pop(key)
    return base


def extract_font_keys(config: Dict[str, Any]) -> Dict[str, Any]:
    """Pop FontConfig keys."""
    font = {}
    for key in KNOWN_GROUPS["font"]["keys"]:
        if key in config:
            font[key] = config.pop(key)
    return font


def extract_position_keys(config: Dict[str, Any]) -> Dict[str, Any]:
    """Pop PositionConfig keys."""
    pos = {}
    for key in KNOWN_GROUPS["position"]["keys"]:
        if key in config:
            pos[key] = config.pop(key)
    return pos


def _find_cell_suffixes(config: Dict[str, Any]) -> Set[str]:
    """Vind suffixen die Cells vormen (2+ attrs uit bekende cell prefixes).

    Cell prefixes: font_color_, bkg_color_, caption_text_, decimal_places_,
    column_index_, show_, prefix_, suffix_.
    """
    cell_prefixes = [
        "font_color_", "bkg_color_", "caption_text_", "decimal_places_",
        "column_index_", "show_", "prefix_", "suffix_",
    ]

    # Tel per suffix hoeveel verschillende prefix-types matchen
    suffix_attrs: Dict[str, Set[str]] = {}
    for key in config:
        for cp in cell_prefixes:
            if key.startswith(cp):
                suffix = key[len(cp):]
                if suffix not in suffix_attrs:
                    suffix_attrs[suffix] = set()
                suffix_attrs[suffix].add(cp)
                break

    # Cell = suffix met 2+ attrs EN minstens font_color of bkg_color
    color_prefixes = {"font_color_", "bkg_color_"}
    return {
        suffix for suffix, attrs in suffix_attrs.items()
        if len(attrs) >= 2 and attrs & color_prefixes
    }


def extract_cells(config: Dict[str, Any]) -> List[Dict]:
    """Haalt Cell definities uit config. Popt alle gematchte keys."""
    cell_suffixes = _find_cell_suffixes(config)

    cells = []
    for cell_id in sorted(cell_suffixes):
        kwargs = {"id": cell_id}

        # Pop alle bekende cell attrs
        cell_attrs = [
            ("font_color", f"font_color_{cell_id}"),
            ("bkg_color", f"bkg_color_{cell_id}"),
            ("caption_text", f"caption_text_{cell_id}"),
            ("decimal_places", f"decimal_places_{cell_id}"),
            ("column_index", f"column_index_{cell_id}"),
            ("show", f"show_{cell_id}"),
            ("prefix", f"prefix_{cell_id}"),
            ("suffix", f"suffix_{cell_id}"),
        ]
        for attr, key in cell_attrs:
            if key in config:
                kwargs[attr] = config.pop(key)

        cells.append(
            {
                "safe_id": _safe_id(cell_id),
                "kwargs": kwargs,
                "kwargs_str": ", ".join(f"{k}={repr(v)}" for k, v in kwargs.items()),
            }
        )

    return cells


def extract_columns(config: Dict[str, Any]) -> List[Dict]:
    """Haalt layout kolom definities uit config.

    Alleen column_index + show keys die NIET al door extract_cells gepakt zijn.
    Dit zijn puur layout columns (upper, middle, lower, etc).
    """
    col_ids = set()
    for key in list(config.keys()):
        if key.startswith("column_index_"):
            col_ids.add(key[13:])

    columns = []
    for col_id in sorted(col_ids):
        kwargs = {
            "id": col_id,
            "show": config.pop(f"show_{col_id}", True),
            "column_index": config.pop(f"column_index_{col_id}", 0),
        }

        columns.append(
            {
                "safe_id": _safe_id(col_id),
                "kwargs_str": ", ".join(f"{k}={repr(v)}" for k, v in kwargs.items()),
            }
        )

    return columns


def extract_auto_prefixes(
    config: Dict[str, Any], auto_prefixes: Dict[str, Dict], widget_name: str
) -> Dict[str, Dict]:
    """Pop auto-detected prefix groups uit config."""
    groups = {}
    for prefix, info in auto_prefixes.items():
        if widget_name not in info["widgets"]:
            continue
        prefix_keys = {}
        for key in list(config.keys()):
            if key.startswith(prefix + "_"):
                prefix_keys[key] = config.pop(key)
        if prefix_keys:
            groups[prefix] = {
                "class_name": _class_name(prefix) + "Config",
                "fields": {
                    k[len(prefix) + 1:]: {
                        "safe_id": _safe_id(k[len(prefix) + 1:]),
                        "type_hint": _infer_type(v),
                        "value_repr": repr(v),
                    }
                    for k, v in prefix_keys.items()
                },
            }
    return groups


def prepare(
    name: str,
    config: Dict[str, Any],
    prefix_components: Dict,
    numbered_components: Dict,
    auto_prefixes: Dict = None,
) -> Dict:
    """Bereidt alle data voor één widget template."""
    config = config.copy()  # Niet muteren origineel

    if auto_prefixes is None:
        auto_prefixes = {}

    # 1. Base keys (enable, update_interval, opacity)
    base_keys = extract_base_keys(config)

    # 2. Font keys
    font_keys = extract_font_keys(config)

    # 3. Position keys
    position_keys = extract_position_keys(config)

    # 4. Cells extracten (muteert config - moet vóór columns!)
    cells = extract_cells(config)

    # 5. Kolommen extracten (layout-only, na cells)
    columns = extract_columns(config)

    # 6. Prefix componenten
    components = {}
    for prefix, data in prefix_components.items():
        kwargs = {}
        for key in list(config.keys()):
            if key.startswith(prefix + "_"):
                suffix = key[len(prefix) + 1:]
                kwargs[suffix] = config.pop(key)
        if kwargs:
            components[prefix] = {
                "class_name": prefix.capitalize() + "Config",
                "kwargs_dict": kwargs,
            }

    # 7. Numbered componenten
    numbered = {}
    for base, data in numbered_components.items():
        indices = data.get("indices", [])
        for idx in indices:
            kwargs = {}
            pattern = f"{base}_{idx}_"
            for key in list(config.keys()):
                if key.startswith(pattern):
                    attr = key[len(pattern):]
                    kwargs[attr] = config.pop(key)
            if kwargs:
                kwargs["_class_name"] = base.capitalize()
                if base not in numbered:
                    numbered[base] = {}
                numbered[base][idx] = kwargs

    # 8. Auto-detected prefix groups
    auto_groups = extract_auto_prefixes(config, auto_prefixes, name)

    # 9. Overgebleven attributen
    leftover = []
    for key, value in sorted(config.items()):
        safe_key = _safe_id(key)
        leftover.append(
            {
                "key": key,
                "safe_id": safe_key,
                "type_hint": _infer_type(value),
                "value_repr": repr(value),
                "is_mutable": isinstance(value, (dict, list)),
            }
        )

    return {
        "name": name,
        "class_name": _class_name(name),
        "base_keys": base_keys,
        "font_keys": font_keys,
        "position_keys": position_keys,
        "cells": cells,
        "columns": columns,
        "components": components,
        "numbered": numbered,
        "auto_groups": auto_groups,
        "leftover_items": leftover,
    }
