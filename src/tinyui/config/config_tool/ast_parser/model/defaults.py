"""Single source of truth voor alle base class defaults.

Gebruikt door:
- model.py (AST dataclass defaults)
- normalize.py (stript default waarden)
- parser.py (weet welke keys bij welke groep horen)
"""

FONT = {
    "font_name": "Consolas",
    "font_size": 15,
    "font_weight": "Bold",
    "font_offset_vertical": 0,
    "font_scale_caption": 0.8,
    "enable_auto_font_offset": True,
}

POSITION = {
    "position_x": 0,
    "position_y": 0,
}

CELL = {
    "font_color": "#FFFFFF",
    "bkg_color": "#222222",
}

WARNING_FLASH = {
    "enabled": True,
    "color": "#FF2200",
    "number_of_flashes": 10,
    "highlight_duration": 0.4,
    "interval": 0.2,
}

BAR = {
    "bar_padding_horizontal": 0.4,
    "bar_padding_vertical": 0.3,
    "bar_width": 50,
    "horizontal_gap": 2,
    "vertical_gap": 2,
    "inner_gap": 0,
}

BASE = {
    "enable": True,
    "update_interval": 20,
    "opacity": 0.9,
    "bar_gap": 2,
    "bar_padding": 0.2,
    "layout": 0,
    "bkg_color": "#222222",
}

# Alle bekende groepen met hun keys
KNOWN_GROUPS = {
    "font": list(FONT.keys()),
    "position": list(POSITION.keys()),
    "bar": list(BAR.keys()),
    "base": list(BASE.keys()),
}

# Bekende cell-prefix patronen
CELL_PREFIXES = [
    "font_color_",
    "bkg_color_",
    "show_",
    "column_index_",
    "decimal_places_",
    "prefix_",
    "suffix_",
    "caption_text_",
]
