"""Theme loading — reads TOML tokens, fills QSS template."""

import os
import sys
import tomllib
from string import Template


def _themes_dir() -> str:
    if getattr(sys, "frozen", False):
        # Frozen build: themes/ next to .exe
        return os.path.join(os.path.dirname(sys.executable), "themes")
    return os.path.dirname(os.path.abspath(__file__))


def load_theme(name: str, base_font_pt: int = 10) -> str:
    """Load a theme TOML and return the filled QSS stylesheet."""
    themes_dir = _themes_dir()
    theme_path = os.path.join(themes_dir, f"{name.lower()}.toml")
    qss_path = os.path.join(themes_dir, "window.qss")

    with open(theme_path, "rb") as f:
        theme = tomllib.load(f)

    with open(qss_path, "r", encoding="utf-8") as f:
        template = Template(f.read())

    colors = theme.get("colors", {})
    font = theme.get("font", {})

    # Build token map for QSS substitution
    # TOML uses dashes, QSS template uses underscores
    tokens = {
        k.replace("-", "_"): v
        for k, v in colors.items()
    }

    # Font sizes from base
    tokens["font_title"] = round(font.get("scale-title", 1.2) * base_font_pt, 1)
    tokens["font_button"] = round(font.get("scale-button", 1.05) * base_font_pt, 1)
    tokens["font_small"] = round(font.get("scale-small", 0.9) * base_font_pt, 1)

    return template.substitute(tokens)
