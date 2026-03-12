"""Bereidt widget data voor templates."""

import keyword
import re
from typing import Any, Dict, List

from flat_to_nested.scan.keys import is_column


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


def extract_columns(config: Dict[str, Any], column_patterns: List[str]) -> List[Dict]:
    """Haalt kolom definities uit config."""
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

        # Optionele attributen
        opt_attrs = [
            ("font_color", f"font_color_{col_id}"),
            ("bkg_color", f"bkg_color_{col_id}"),
            ("decimal_places", f"decimal_places_{col_id}"),
            ("prefix", f"prefix_{col_id}"),
            ("suffix", f"suffix_{col_id}"),
        ]
        for attr, key in opt_attrs:
            if key in config:
                kwargs[attr] = config.pop(key)

        # Thresholds
        low_key = f"low_{col_id}_threshold"
        high_key = f"high_{col_id}_threshold"
        if low_key in config or high_key in config:
            kwargs["low_threshold"] = config.pop(low_key, None)
            kwargs["high_threshold"] = config.pop(high_key, None)

        # Warning colors
        wl_key = f"warning_color_low_{col_id}"
        wh_key = f"warning_color_high_{col_id}"
        if wl_key in config:
            kwargs["warning_color_low"] = config.pop(wl_key)
        if wh_key in config:
            kwargs["warning_color_high"] = config.pop(wh_key)

        # Flash settings
        flash_key = f"show_{col_id}_warning_flash"
        if config.get(flash_key, False):
            kwargs["warning_flash"] = True
            kwargs["flash_count"] = config.pop(
                f"number_of_{col_id}_warning_flashes", 10
            )
            kwargs["flash_duration"] = config.pop(
                f"{col_id}_warning_flash_duration", 0.4
            )
            kwargs["flash_interval"] = config.pop(
                f"{col_id}_warning_flash_interval", 0.2
            )
            config.pop(flash_key, None)

        columns.append(
            {
                "safe_id": _safe_id(col_id),
                "kwargs_str": ", ".join(f"{k}={repr(v)}" for k, v in kwargs.items()),
            }
        )

    return columns


def prepare(
    name: str,
    config: Dict[str, Any],
    prefix_components: Dict,
    numbered_components: Dict,
) -> Dict:
    """Bereidt alle data voor één widget template."""
    config = config.copy()  # Niet muteren origineel

    # Kolommen extracten (mutatert config)
    columns = extract_columns(config, [])

    # Prefix componenten
    components = {}
    for prefix, data in prefix_components.items():
        kwargs = {}
        for key in list(config.keys()):
            if key.startswith(prefix + "_"):
                suffix = key[len(prefix) + 1 :]
                kwargs[suffix] = config.pop(key)
        if kwargs:
            components[prefix] = {
                "class_name": prefix.capitalize() + "Config",
                "kwargs_dict": kwargs,
            }

    # Numbered componenten
    numbered = {}
    for base, data in numbered_components.items():
        indices = data.get("indices", [])
        for idx in indices:
            kwargs = {}
            pattern = f"{base}_{idx}_"
            for key in list(config.keys()):
                if key.startswith(pattern):
                    attr = key[len(pattern) :]
                    kwargs[attr] = config.pop(key)
            if kwargs:
                kwargs["_class_name"] = base.capitalize()
                if base not in numbered:
                    numbered[base] = {}
                numbered[base][idx] = kwargs

    # Overgebleven attributen
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
        "columns": columns,
        "components": components,
        "numbered": numbered,
        "leftover_items": leftover,
    }
