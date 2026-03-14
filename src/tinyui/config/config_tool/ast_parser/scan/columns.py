"""Kolom en cell detectie per widget."""

from typing import Any, Dict, List, Optional, Set

from ..model import CELL_PREFIXES


def extract_column_suffixes(keys: List[str]) -> Set[str]:
    """Haal kolom suffixen op uit column_index_ keys."""
    suffixes = set()
    for key in keys:
        if key.startswith("column_index_"):
            suffix = key[13:]
            suffixes.add(suffix)
    return suffixes


def find_show_key(suffix: str, keys: List[str]) -> Optional[str]:
    """Vind show_key die bij een suffix hoort."""
    show_keys = [k for k in keys if k.startswith("show_")]

    exact = f"show_{suffix}"
    if exact in show_keys:
        return exact

    for sk in show_keys:
        show_part = sk[5:]
        if suffix in show_part or show_part in suffix:
            return sk

    best_match = None
    best_score = 0
    for sk in show_keys:
        show_part = sk[5:]
        score = len(set(suffix.split("_")) & set(show_part.split("_")))
        if score > best_score:
            best_score = score
            best_match = sk

    return best_match


def find_state_colors(suffix: str, keys: List[str]) -> Dict[str, str]:
    """Vind state color keys die bij een kolom horen."""
    states = {}
    for key in keys:
        if key.startswith(f"font_color_{suffix}_"):
            state = key[len(f"font_color_{suffix}_"):]
            states[f"font_color_{state}"] = key
        elif key.startswith(f"bkg_color_{suffix}_"):
            state = key[len(f"bkg_color_{suffix}_"):]
            states[f"bkg_color_{state}"] = key
    return states


def collect_column_keys(suffix: str, show_key: str, keys: List[str]) -> Dict:
    """Verzamel alle keys die bij een kolom horen."""
    result = {
        "id": suffix,
        "show_key": show_key,
        "column_index": f"column_index_{suffix}",
    }

    font_key = f"font_color_{suffix}"
    bkg_key = f"bkg_color_{suffix}"
    if font_key in keys:
        result["font_color"] = font_key
    if bkg_key in keys:
        result["bkg_color"] = bkg_key

    optional = {
        "decimal_places": f"decimal_places_{suffix}",
        "prefix": f"prefix_{suffix}",
        "suffix_attr": f"suffix_{suffix}",
        "low_threshold": f"low_{suffix}_threshold",
        "high_threshold": f"high_{suffix}_threshold",
        "warning_color_low": f"warning_color_low_{suffix}",
        "warning_color_high": f"warning_color_high_{suffix}",
        "show_warning_flash": f"show_{suffix}_warning_flash",
        "number_of_warning_flashes": f"number_of_{suffix}_warning_flashes",
        "warning_flash_duration": f"{suffix}_warning_flash_duration",
        "warning_flash_interval": f"{suffix}_warning_flash_interval",
    }

    for attr, pattern in optional.items():
        if pattern in keys:
            result[attr] = pattern

    state_colors = find_state_colors(suffix, keys)
    if state_colors:
        result["state_colors"] = state_colors

    return result


def analyze_widget_columns(widget_name: str, config: Dict[str, any]) -> List[Dict]:
    """Analyseer alle kolommen in één widget."""
    keys = list(config.keys())
    suffixes = extract_column_suffixes(keys)

    columns = []
    for suffix in sorted(suffixes):
        show_key = find_show_key(suffix, keys)
        if not show_key:
            show_key = f"show_{suffix}"
        column_data = collect_column_keys(suffix, show_key, keys)
        columns.append(column_data)

    def get_index(col):
        idx_key = col["column_index"]
        return config.get(idx_key, 0)

    return sorted(columns, key=get_index)


def analyze_all_columns(configs: Dict[str, Dict]) -> Dict[str, List[Dict]]:
    """Analyseer kolommen voor alle widgets."""
    return {name: analyze_widget_columns(name, config) for name, config in configs.items()}


def extract_cell_suffixes(config: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Detecteer cell suffixen: suffixen met 2+ attrs EN minstens font/bkg_color."""
    suffix_attrs: Dict[str, Dict[str, str]] = {}

    for key in config:
        for cp in CELL_PREFIXES:
            if key.startswith(cp):
                suffix = key[len(cp):]
                attr = cp.rstrip("_")
                if suffix not in suffix_attrs:
                    suffix_attrs[suffix] = {}
                suffix_attrs[suffix][attr] = key
                break

    color_attrs = {"font_color", "bkg_color"}
    return {
        suffix: attrs
        for suffix, attrs in suffix_attrs.items()
        if len(attrs) >= 2 and set(attrs.keys()) & color_attrs
    }


def analyze_widget_cells(widget_name: str, config: Dict[str, Any]) -> List[Dict]:
    """Analyseer alle cells in één widget."""
    cells_data = extract_cell_suffixes(config)

    cells = []
    for suffix in sorted(cells_data.keys()):
        attrs = cells_data[suffix]
        cell = {
            "id": suffix,
            "attrs": sorted(attrs.keys()),
            "keys": attrs,
        }

        if "caption_text" in attrs:
            cell["variant"] = "caption"
        elif "column_index" in attrs:
            cell["variant"] = "column"
        else:
            cell["variant"] = "basic"

        cells.append(cell)

    return cells


def analyze_all_cells(configs: Dict[str, Dict]) -> Dict[str, List[Dict]]:
    """Analyseer cells voor alle widgets."""
    return {
        name: analyze_widget_cells(name, config)
        for name, config in configs.items()
    }
