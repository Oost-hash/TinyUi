"""Bereidt color palette data voor templates."""

import re
from typing import Dict, List


def _to_palette_name(font: str, bkg: str, index: int) -> str:
    """Genereer een leesbare naam voor een palette."""
    # Bekende combinaties
    known = {
        ("#FFFFFF", "#222222"): "DEFAULT",
        ("#000000", "#BBBBBB"): "LIGHT_ON_MEDIUM",
        ("#CCCCCC", "#777777"): "CAPTION",
        ("#DDDDDD", "#666666"): "MUTED",
        ("#AAAAAA", "#2A2A2A"): "SUBTLE_DARK",
        ("#000000", "#DDDDDD"): "DARK_ON_LIGHT",
        ("#AAAAAA", "#222222"): "SUBTLE",
        ("#000000", "#FFFFFF"): "BLACK_ON_WHITE",
        ("#AAAAAA", "#333333"): "SUBTLE_MID",
        ("#555555", "#FFFFFF"): "DIM_ON_WHITE",
        ("#000000", "#CCCCCC"): "DARK_ON_SILVER",
        ("#222222", "#EEEEEE"): "DARK_ON_BRIGHT",
        ("#FFFFFF", "#333333"): "WHITE_ON_DARK",
        ("#000000", "#222222"): "BLACK_ON_DARK",
        ("#CCCCCC", "#222222"): "SILVER_ON_DARK",
        ("#DDDDDD", "#333333"): "LIGHT_ON_MID",
        ("#222222", "#CCCCCC"): "DARK_ON_SILVER_ALT",
        ("#000000", "#FFFF00"): "WARNING_YELLOW",
        ("#666666", "#222222"): "GRAY_ON_DARK",
        ("#FFFF00", "#000000"): "YELLOW_FLAG",
    }

    key = (font, bkg)
    if key in known:
        return known[key]

    return f"PALETTE_{index}"


def prepare(global_palettes: List[Dict], min_count: int = 2) -> List[Dict]:
    """Maak palette data voor de colors template.

    Alleen palettes die in min_count+ widgets voorkomen worden opgenomen.
    Unieke kleuren blijven in de widget zelf.

    Args:
        global_palettes: output van analyze_all_colors()["global_palettes"]
        min_count: minimum aantal keer dat een palette moet voorkomen

    Returns:
        Lijst van palette dicts met name, font_color, bkg_color, count.
    """
    result = []
    used_names = set()

    for i, entry in enumerate(global_palettes):
        if entry["count"] < min_count:
            continue

        name = _to_palette_name(entry["font_color"], entry["bkg_color"], i)

        # Zorg voor unieke namen
        if name in used_names:
            name = f"{name}_{i}"
        used_names.add(name)

        result.append({
            "name": name,
            "font_color": entry["font_color"],
            "bkg_color": entry["bkg_color"],
            "count": entry["count"],
        })

    return result
