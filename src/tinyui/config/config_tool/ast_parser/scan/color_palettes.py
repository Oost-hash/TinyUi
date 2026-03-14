"""Kleur palette detectie over widget configuraties."""

import re
from collections import Counter
from typing import Any, Dict, List, Tuple

HEX_PATTERN = re.compile(r"^#(?:[0-9a-fA-F]{3}){1,2}$")


def is_hex_color(value: Any) -> bool:
    """Check of een waarde een hex kleurcode is."""
    return isinstance(value, str) and bool(HEX_PATTERN.match(value))


def extract_color_keys(config: Dict[str, Any]) -> List[Tuple[str, str]]:
    """Vind alle keys met hex waarden in een widget config."""
    return [(key, value) for key, value in config.items() if is_hex_color(value)]


def extract_color_pairs(config: Dict[str, Any]) -> List[Dict]:
    """Vind font_color + bkg_color paren op basis van gedeeld suffix."""
    font_colors = {}
    bkg_colors = {}

    for key, value in config.items():
        if not is_hex_color(value):
            continue
        if key.startswith("font_color_"):
            suffix = key[11:]
            font_colors[suffix] = value.upper()
        elif key.startswith("bkg_color_"):
            suffix = key[10:]
            bkg_colors[suffix] = value.upper()

    pairs = []
    all_suffixes = sorted(set(font_colors) | set(bkg_colors))

    for suffix in all_suffixes:
        pair = {"suffix": suffix}
        if suffix in font_colors:
            pair["font_color"] = font_colors[suffix]
        if suffix in bkg_colors:
            pair["bkg_color"] = bkg_colors[suffix]
        pairs.append(pair)

    return pairs


def match_unpaired_to_palette(
    unpaired: List[Dict], known_palettes: List[Tuple[str, str]]
) -> tuple:
    """Match ongepaarde kleuren aan bekende palettes."""
    by_font = {}
    by_bkg = {}
    for font, bkg in known_palettes:
        by_font.setdefault(font, []).append((font, bkg))
        by_bkg.setdefault(bkg, []).append((font, bkg))

    matched = []
    still_unpaired = []

    for entry in unpaired:
        suffix = entry["suffix"]
        font = entry.get("font_color")
        bkg = entry.get("bkg_color")

        match = None
        if bkg and not font and bkg in by_bkg:
            candidates = by_bkg[bkg]
            match = {"font_color": candidates[0][0], "bkg_color": candidates[0][1]}
        elif font and not bkg and font in by_font:
            candidates = by_font[font]
            match = {"font_color": candidates[0][0], "bkg_color": candidates[0][1]}

        if match:
            matched.append({
                "suffix": suffix,
                "matched_palette": match,
                "had": "bkg_color" if bkg else "font_color",
                "original": bkg or font,
            })
        else:
            still_unpaired.append(entry)

    return matched, still_unpaired


def analyze_widget_colors(widget_name: str, config: Dict[str, Any]) -> Dict:
    """Analyseer kleuren voor één widget."""
    color_keys = extract_color_keys(config)
    pairs = extract_color_pairs(config)

    unique_colors = sorted(set(v.upper() for _, v in color_keys))
    complete_pairs = [p for p in pairs if "font_color" in p and "bkg_color" in p]
    unpaired = [p for p in pairs if "font_color" not in p or "bkg_color" not in p]

    return {
        "widget": widget_name,
        "unique_colors": unique_colors,
        "color_count": len(unique_colors),
        "pairs": complete_pairs,
        "unpaired": unpaired,
    }


def analyze_all_colors(configs: Dict[str, Dict]) -> Dict:
    """Analyseer kleur palettes over alle widgets."""
    palette_counter = Counter()
    color_counter = Counter()
    per_widget_raw = {}

    for name, config in configs.items():
        widget_result = analyze_widget_colors(name, config)
        per_widget_raw[name] = widget_result

        for color in widget_result["unique_colors"]:
            color_counter[color] += 1

        for pair in widget_result["pairs"]:
            palette_key = (pair["font_color"], pair["bkg_color"])
            palette_counter[palette_key] += 1

    sorted_palettes = [p for p, _ in palette_counter.most_common()]

    per_widget = {}
    total_matched = 0
    total_still_unpaired = 0

    for name, widget_result in per_widget_raw.items():
        matched, still_unpaired = match_unpaired_to_palette(
            widget_result["unpaired"], sorted_palettes
        )
        per_widget[name] = {
            **widget_result,
            "matched": matched,
            "unpaired": still_unpaired,
        }
        total_matched += len(matched)
        total_still_unpaired += len(still_unpaired)

    global_palettes = [
        {"font_color": font, "bkg_color": bkg, "count": count}
        for (font, bkg), count in palette_counter.most_common()
    ]

    return {
        "per_widget": per_widget,
        "global_palettes": global_palettes,
        "total_unique_palettes": len(palette_counter),
        "total_unique_colors": len(color_counter),
        "total_matched": total_matched,
        "total_still_unpaired": total_still_unpaired,
    }
