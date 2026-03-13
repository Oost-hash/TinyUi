"""Post-processing stappen na widget build.

Aparte stap die gebouwde widget data opschoont: default waarden
verwijderen zodat classes hun eigen defaults gebruiken.
"""

from typing import Any, Dict, List


# Moet overeenkomen met classes in base.py.j2
CELL_DEFAULTS = {
    "font_color": "#FFFFFF",
    "bkg_color": "#222222",
}

FONT_DEFAULTS = {
    "font_name": "Consolas",
    "font_size": 15,
    "font_weight": "Bold",
    "font_offset_vertical": 0,
    "font_scale_caption": 0.8,
    "enable_auto_font_offset": True,
}

POSITION_DEFAULTS = {
    "position_x": 0,
    "position_y": 0,
}

BASE_DEFAULTS = {
    "enable": True,
    "update_interval": 20,
    "opacity": 0.9,
    "bar_gap": 2,
    "bar_padding": 0.2,
}


def _rebuild_kwargs_str(kwargs: Dict[str, Any]) -> str:
    """Render kwargs dict naar constructor string."""
    return ", ".join(f"{k}={repr(v)}" for k, v in kwargs.items())


def _strip_defaults(data: Dict[str, Any], defaults: Dict[str, Any]) -> bool:
    """Verwijder entries die gelijk zijn aan defaults. Returns True als er iets veranderd is."""
    changed = False
    for attr, default_value in defaults.items():
        if attr in data and data[attr] == default_value:
            del data[attr]
            changed = True
    return changed


def strip_default_colors(widget_data: Dict) -> Dict:
    """Verwijder default kleuren uit cells."""
    for cell in widget_data.get("cells", []):
        if _strip_defaults(cell["kwargs"], CELL_DEFAULTS):
            cell["kwargs_str"] = _rebuild_kwargs_str(cell["kwargs"])
    return widget_data


def strip_default_config(widget_data: Dict) -> Dict:
    """Verwijder default waarden uit font, position en base keys."""
    _strip_defaults(widget_data.get("font_keys", {}), FONT_DEFAULTS)
    _strip_defaults(widget_data.get("position_keys", {}), POSITION_DEFAULTS)
    _strip_defaults(widget_data.get("base_keys", {}), BASE_DEFAULTS)
    return widget_data


def post_process(widget_data: Dict) -> Dict:
    """Voer alle post-processing stappen uit op een widget."""
    widget_data = strip_default_colors(widget_data)
    widget_data = strip_default_config(widget_data)
    return widget_data
