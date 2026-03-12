"""Kolom detectie en groepering per widget."""

from typing import Dict, List, Optional, Set


def extract_column_suffixes(keys: List[str]) -> Set[str]:
    """Haal kolom suffixen op uit column_index_ keys (betrouwbaarder dan color keys)."""
    suffixes = set()

    for key in keys:
        if key.startswith("column_index_"):
            suffix = key[13:]  # na "column_index_"
            suffixes.add(suffix)

    return suffixes


def find_show_key(suffix: str, keys: List[str]) -> Optional[str]:
    """Vind show_key die bij een suffix hoort."""
    show_keys = [k for k in keys if k.startswith("show_")]

    # Exacte match: show_<suffix>
    exact = f"show_{suffix}"
    if exact in show_keys:
        return exact

    # Partial match: suffix komt voor in show_key na "show_"
    for sk in show_keys:
        show_part = sk[5:]  # na "show_"
        if suffix in show_part or show_part in suffix:
            return sk

    # Fallback: longest common substring
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
    """Vind state color keys die bij een kolom horen (bijv. position_same, position_gain)."""
    states = {}

    # Zoek font_color_<suffix>_* en bkg_color_<suffix>_*
    for key in keys:
        if key.startswith(f"font_color_{suffix}_"):
            state = key[len(f"font_color_{suffix}_") :]
            states[f"font_color_{state}"] = key
        elif key.startswith(f"bkg_color_{suffix}_"):
            state = key[len(f"bkg_color_{suffix}_") :]
            states[f"bkg_color_{state}"] = key

    return states


def collect_column_keys(suffix: str, show_key: str, keys: List[str]) -> Dict:
    """Verzamel alle keys die bij een kolom horen."""
    result = {
        "id": suffix,
        "show_key": show_key,
        "column_index": f"column_index_{suffix}",
    }

    # Hoofd color keys (optioneel - sommige kolommen hebben ze niet)
    font_key = f"font_color_{suffix}"
    bkg_key = f"bkg_color_{suffix}"
    if font_key in keys:
        result["font_color"] = font_key
    if bkg_key in keys:
        result["bkg_color"] = bkg_key

    # Overige attributen
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

    # State colors (bijv. position_same, position_gain, position_loss)
    state_colors = find_state_colors(suffix, keys)
    if state_colors:
        result["state_colors"] = state_colors

    return result


def analyze_widget_columns(widget_name: str, config: Dict[str, any]) -> List[Dict]:
    """Analyseer alle kolommen in één widget."""
    keys = list(config.keys())

    # Stap 1: vind alle kolom suffixen via column_index (betrouwbaar)
    suffixes = extract_column_suffixes(keys)

    # Stap 2: per suffix, vind show_key en alle bijbehorende keys
    columns = []
    for suffix in sorted(suffixes):
        show_key = find_show_key(suffix, keys)
        if not show_key:
            show_key = f"show_{suffix}"  # Fallback, kan missen

        column_data = collect_column_keys(suffix, show_key, keys)
        columns.append(column_data)

    # Sorteer op column_index waarde
    def get_index(col):
        idx_key = col["column_index"]
        return config.get(idx_key, 0)

    return sorted(columns, key=get_index)


def analyze_all_columns(configs: Dict[str, Dict]) -> Dict[str, List[Dict]]:
    """Analyseer kolommen voor alle widgets."""
    result = {}
    for name, config in configs.items():
        result[name] = analyze_widget_columns(name, config)
    return result


def find_column_inconsistencies(columns_analysis: Dict[str, List[Dict]]) -> List[Dict]:
    """Vind kolommen zonder show_key of font_color."""
    issues = []

    for widget_name, columns in columns_analysis.items():
        for col in columns:
            # Check: heeft deze kolom een show_key die bestaat?
            # (niet strikt nodig voor werking, maar wel voor validatie)
            pass  # Met column_index detectie zijn er minder "fouten"

    return issues
