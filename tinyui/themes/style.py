#
#  TinyUi - Theme Style
#  Copyright (C) 2025 Oost-hash
#

"""Palette and stylesheet loading."""

import json
import os
import sys
from string import Template

from PySide2.QtGui import QGuiApplication, QPalette
from PySide2.QtWidgets import QApplication

_ROLE_MAP = {
    "Window": QPalette.Window,
    "WindowText": QPalette.WindowText,
    "Base": QPalette.Base,
    "AlternateBase": QPalette.AlternateBase,
    "ToolTipBase": QPalette.ToolTipBase,
    "ToolTipText": QPalette.ToolTipText,
    "PlaceholderText": QPalette.PlaceholderText,
    "Text": QPalette.Text,
    "Button": QPalette.Button,
    "ButtonText": QPalette.ButtonText,
    "BrightText": QPalette.BrightText,
    "Light": QPalette.Light,
    "Midlight": QPalette.Midlight,
    "Dark": QPalette.Dark,
    "Mid": QPalette.Mid,
    "Shadow": QPalette.Shadow,
    "Highlight": QPalette.Highlight,
    "HighlightedText": QPalette.HighlightedText,
    "Link": QPalette.Link,
    "LinkVisited": QPalette.LinkVisited,
}

_THEMES_DIR = os.path.dirname(os.path.abspath(__file__))
_QSS_FILE = os.path.join(_THEMES_DIR, "window.qss")


def _themes_dir() -> str:
    """Resolve themes directory, works both frozen (py2exe) and development."""
    if getattr(sys, "frozen", False):
        return os.path.join(os.path.dirname(sys.executable), "tinyui", "themes")
    return _THEMES_DIR


def load_theme(name: str) -> list:
    """Load theme palette from JSON file in themes/ folder."""
    theme_path = os.path.join(_themes_dir(), f"{name.lower()}.json")
    with open(theme_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    palette_data = data["palette"]
    result = []
    for role_name, colors in palette_data.items():
        role = _ROLE_MAP[role_name]
        result.append((colors["active"], colors["inactive"], colors["disabled"], role))
    return result


def set_style_palette(color_theme: str):
    """Set style palette from theme JSON."""
    palette_theme = load_theme(color_theme)
    palette = QGuiApplication.palette()
    group_active = QPalette.Active
    group_inactive = QPalette.Inactive
    group_disabled = QPalette.Disabled
    for color_active, color_inactive, color_disabled, color_role in palette_theme:
        palette.setColor(group_active, color_role, color_active)
        palette.setColor(group_inactive, color_role, color_inactive)
        palette.setColor(group_disabled, color_role, color_disabled)
    QApplication.setPalette(palette)


def set_style_window(base_font_pt: int) -> str:
    """Load QSS template and fill in palette colors and font sizes."""
    # Font sizes
    font_pt_item_name = 1.2 * base_font_pt
    font_pt_item_button = 1.05 * base_font_pt
    font_pt_item_toggle = 1.0 * base_font_pt
    font_pt_text_browser = 0.9 * base_font_pt
    font_pt_app_name = 1.4 * base_font_pt

    # Sizes
    border_radius_button = 0.1  # em

    # Palette colors
    palette = QApplication.palette()
    palette.setCurrentColorGroup(QPalette.Active)
    color_active_window_text = palette.windowText().color().name()
    color_active_window = palette.window().color().name()
    color_active_base = palette.base().color().name()
    color_active_highlighted_text = palette.highlightedText().color().name()
    color_active_highlight = palette.highlight().color().name()

    palette.setCurrentColorGroup(QPalette.Inactive)
    color_inactive_highlighted_text = palette.highlightedText().color().name()
    color_inactive_highlight = palette.highlight().color().name()

    palette.setCurrentColorGroup(QPalette.Disabled)
    color_disabled_window_text = palette.windowText().color().name()
    color_disabled_highlighted_text = palette.highlightedText().color().name()
    color_disabled_highlight = palette.highlight().color().name()

    # Load and fill QSS template
    with open(_QSS_FILE, "r", encoding="utf-8") as f:
        template = Template(f.read())

    return template.substitute(
        font_pt_item_name=font_pt_item_name,
        font_pt_item_button=font_pt_item_button,
        font_pt_item_toggle=font_pt_item_toggle,
        font_pt_text_browser=font_pt_text_browser,
        font_pt_app_name=font_pt_app_name,
        border_radius_button=border_radius_button,
        color_active_window_text=color_active_window_text,
        color_active_window=color_active_window,
        color_active_base=color_active_base,
        color_active_highlighted_text=color_active_highlighted_text,
        color_active_highlight=color_active_highlight,
        color_inactive_highlighted_text=color_inactive_highlighted_text,
        color_inactive_highlight=color_inactive_highlight,
        color_disabled_window_text=color_disabled_window_text,
        color_disabled_highlighted_text=color_disabled_highlighted_text,
        color_disabled_highlight=color_disabled_highlight,
    )
