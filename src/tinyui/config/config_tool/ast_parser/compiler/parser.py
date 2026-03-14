"""Pattern Parser - vervangt alle extract_* functies.

Eén engine die flat config keys classificeert via een pattern registry.
Elke pattern rule popt matching keys en produceert AST nodes.
"""

from __future__ import annotations

import re
from collections import Counter
from typing import Any

from ..model import CELL_PREFIXES, KNOWN_GROUPS
from ..model import (
    Cell,
    Component,
    ComponentInstance,
    Field,
    WarningFlash,
    WidgetAST,
)
from ..utils import infer_type, safe_id, to_class_name


# ---------------------------------------------------------------------------
# Pattern rules - elk popt keys uit config en retourneert data
# ---------------------------------------------------------------------------

def _parse_known_group(config: dict[str, Any], group_name: str) -> dict[str, Any]:
    """Pop keys voor een bekende groep (font, position, bar, base)."""
    result = {}
    for key in KNOWN_GROUPS[group_name]:
        if key in config:
            result[key] = config.pop(key)
    return result


def _parse_cells(config: dict[str, Any]) -> list[Cell]:
    """Detecteer en pop Cell patronen (font_color_X, bkg_color_X, etc.)."""
    suffix_attrs: dict[str, set[str]] = {}
    for key in config:
        for cp in CELL_PREFIXES:
            if key.startswith(cp):
                suffix = key[len(cp):]
                if suffix not in suffix_attrs:
                    suffix_attrs[suffix] = set()
                suffix_attrs[suffix].add(cp)
                break

    # Cell = suffix met 2+ attrs EN minstens font_color of bkg_color
    color_prefixes = {"font_color_", "bkg_color_"}
    cell_ids = {
        suffix for suffix, attrs in suffix_attrs.items()
        if len(attrs) >= 2 and attrs & color_prefixes
    }

    cell_attrs_map = [
        ("font_color", "font_color_"),
        ("bkg_color", "bkg_color_"),
        ("caption_text", "caption_text_"),
        ("decimal_places", "decimal_places_"),
        ("column_index", "column_index_"),
        ("show", "show_"),
        ("prefix", "prefix_"),
        ("suffix", "suffix_"),
    ]

    cells = []
    for cell_id in sorted(cell_ids):
        attrs = {}
        for attr, prefix in cell_attrs_map:
            key = f"{prefix}{cell_id}"
            if key in config:
                attrs[attr] = config.pop(key)

        cells.append(Cell(id=cell_id, attrs=attrs))

    return cells


def _parse_columns(config: dict[str, Any]) -> list[Cell]:
    """Pop layout kolommen (column_index_X + show_X zonder andere cell attrs)."""
    col_ids = set()
    for key in list(config.keys()):
        if key.startswith("column_index_"):
            col_ids.add(key[13:])

    columns = []
    for col_id in sorted(col_ids):
        attrs = {
            "show": config.pop(f"show_{col_id}", True),
            "column_index": config.pop(f"column_index_{col_id}", 0),
        }
        columns.append(Cell(id=col_id, attrs=attrs))

    return columns


def _parse_warning_flash(config: dict[str, Any]) -> WarningFlash | None:
    """Detecteer en pop WarningFlash keys."""
    if "warning_flash_interval" not in config:
        return None

    attrs = {}
    key_map = {}

    fixed = {
        "number_of_flashes": "number_of_warning_flashes",
        "highlight_duration": "warning_flash_highlight_duration",
        "interval": "warning_flash_interval",
    }
    for attr, flat_key in fixed.items():
        if flat_key in config:
            attrs[attr] = config.pop(flat_key)
            key_map[attr] = flat_key

    for key in list(config.keys()):
        if key.startswith("show_") and key.endswith("_warning_flash"):
            attrs["enabled"] = config.pop(key)
            key_map["enabled"] = key
            break

    for key in sorted(config.keys()):
        if not key.startswith("warning_color_"):
            continue
        suffix = key[14:]
        if suffix.startswith("low_") or suffix.startswith("high_"):
            direction = suffix.split("_")[0]
            attr = "color" if direction == "low" else "color_high"
        else:
            attr = "color"
        attrs[attr] = config.pop(key)
        key_map[attr] = key

    return WarningFlash(attrs=attrs, key_map=key_map)


def _parse_numbered(config: dict[str, Any]) -> list[Component]:
    """Detecteer {prefix}_{N}_{attr} patronen."""
    pattern = re.compile(r'^(.+?)_(\d+)_(.+)$')

    prefix_data: dict[str, dict[int, dict[str, Any]]] = {}
    prefix_keys: dict[str, list[str]] = {}

    for key in list(config.keys()):
        m = pattern.match(key)
        if not m:
            continue
        prefix, idx, attr = m.group(1), int(m.group(2)), m.group(3)
        if prefix not in prefix_data:
            prefix_data[prefix] = {}
            prefix_keys[prefix] = []
        if idx not in prefix_data[prefix]:
            prefix_data[prefix][idx] = {}
        prefix_data[prefix][idx][attr] = config[key]
        prefix_keys[prefix].append(key)

    components = []
    for prefix in sorted(prefix_data):
        indices = prefix_data[prefix]
        if len(indices) < 2:
            continue

        for key in prefix_keys[prefix]:
            config.pop(key, None)

        # Type inference + defaults via Counter
        all_values: dict[str, list] = {}
        for idx_data in indices.values():
            for attr, val in idx_data.items():
                all_values.setdefault(attr, []).append(val)

        fields = []
        defaults = {}
        for attr in sorted(all_values):
            values = all_values[attr]
            typ = infer_type(values[0])
            default = Counter(values).most_common(1)[0][0]
            fields.append(Field(name=attr, type=typ, default=default))
            defaults[attr] = default

        instances = [
            ComponentInstance(key=idx, attrs=dict(sorted(indices[idx].items())))
            for idx in sorted(indices)
        ]

        components.append(Component(
            class_name=to_class_name(prefix),
            kind="numbered",
            prefix=prefix,
            fields=fields,
            defaults=defaults,
            instances=instances,
        ))

    return components


def _parse_json_groupings(
    config: dict[str, Any],
    widget_groupings: dict[str, dict],
) -> list[Component]:
    """Parse groupings uit JSON definitie (numbered + prefixed)."""
    components = []

    for class_name, spec in widget_groupings.items():
        attrs_list = spec["attrs"]
        reverse_attrs_list = spec.get("reverse_attrs", [])
        all_attrs = attrs_list + reverse_attrs_list

        if "numbered" in spec:
            instances = _extract_numbered_from_spec(
                config, spec["numbered"], attrs_list
            )
            kind = "numbered"
            prefix = spec["numbered"]
        elif "instances" in spec:
            instances = _extract_prefixed_from_spec(
                config, spec["instances"], attrs_list, reverse_attrs_list
            )
            kind = "prefixed"
            prefix = ""
        else:
            continue

        if not instances:
            continue

        all_values: dict[str, list] = {attr: [] for attr in all_attrs}
        for inst in instances:
            for attr, val in inst.attrs.items():
                all_values[attr].append(val)

        fields = []
        defaults = {}
        for attr in all_attrs:
            values = all_values[attr]
            if not values:
                continue
            typ = infer_type(values[0])
            default = Counter(values).most_common(1)[0][0]
            fields.append(Field(name=attr, type=typ, default=default))
            defaults[attr] = default

        components.append(Component(
            class_name=class_name,
            kind=kind,
            prefix=prefix,
            fields=fields,
            defaults=defaults,
            reverse_attrs=set(reverse_attrs_list),
            instances=instances,
        ))

    return components


def _extract_numbered_from_spec(
    config: dict[str, Any], prefix: str, attrs_list: list[str]
) -> list[ComponentInstance]:
    """Extracteer {prefix}_{N}_{attr} keys voor een JSON grouping spec."""
    pattern = re.compile(rf'^{re.escape(prefix)}_(\d+)_(.+)$')
    indices: dict[int, dict[str, Any]] = {}
    matched_keys: list[str] = []

    for key in list(config.keys()):
        m = pattern.match(key)
        if not m:
            continue
        idx, attr = int(m.group(1)), m.group(2)
        if attr not in attrs_list:
            continue
        indices.setdefault(idx, {})[attr] = config[key]
        matched_keys.append(key)

    if len(indices) < 2:
        return []

    for key in matched_keys:
        config.pop(key, None)

    return [
        ComponentInstance(key=idx, attrs=dict(sorted(indices[idx].items())))
        for idx in sorted(indices)
    ]


def _extract_prefixed_from_spec(
    config: dict[str, Any],
    instance_names: list[str],
    attrs_list: list[str],
    reverse_attrs_list: list[str],
) -> list[ComponentInstance]:
    """Extracteer {instance}_{attr} en {attr}_{instance} keys."""
    instances = []

    for inst_name in instance_names:
        attrs = {}
        for attr in attrs_list:
            key = f"{inst_name}_{attr}"
            if key in config:
                attrs[attr] = config.pop(key)
        for attr in reverse_attrs_list:
            key = f"{attr}_{inst_name}"
            if key in config:
                attrs[attr] = config.pop(key)

        if attrs:
            instances.append(ComponentInstance(key=inst_name, attrs=attrs))

    return instances


# ---------------------------------------------------------------------------
# Hoofdfunctie
# ---------------------------------------------------------------------------

def parse(
    name: str,
    config: dict[str, Any],
    groupings: dict[str, dict] | None = None,
) -> WidgetAST:
    """Parse een flat widget config naar een WidgetAST.

    Args:
        name: widget naam (bijv. "battery")
        config: flat config dict (wordt gekopieerd, niet gemuteerd)
        groupings: optionele JSON grouping specs voor dit widget
    """
    config = config.copy()

    # Bekende groepen
    base_keys = _parse_known_group(config, "base")
    font_keys = _parse_known_group(config, "font")
    position_keys = _parse_known_group(config, "position")
    bar_keys = _parse_known_group(config, "bar")

    # Cells en columns
    cells = _parse_cells(config)
    cells.extend(_parse_columns(config))

    # Warning flash
    warning_flash = _parse_warning_flash(config)

    # Components: JSON groupings eerst, dan auto-detect numbered
    components = []
    if groupings:
        components.extend(_parse_json_groupings(config, groupings))
    components.extend(_parse_numbered(config))

    # Leftover
    leftover = [
        Field(name=safe_id(key), type=infer_type(value), default=value)
        for key, value in sorted(config.items())
    ]

    return WidgetAST(
        name=name,
        base_keys=base_keys,
        font_keys=font_keys,
        position_keys=position_keys,
        bar_keys=bar_keys,
        cells=cells,
        warning_flash=warning_flash,
        components=components,
        leftover=leftover,
    )
