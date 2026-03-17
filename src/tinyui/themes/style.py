#  TinyUI
#  Copyright (C) 2026 Oost-hash
#
#  This file is part of TinyUI.
#
#  TinyUI is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  TinyUI is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#  TinyUI builds on TinyPedal by s-victor (https://github.com/s-victor/TinyPedal),
#  licensed under GPLv3.

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
    tokens = {k.replace("-", "_"): v for k, v in colors.items()}

    # Font sizes from base
    tokens["font_title"] = round(font.get("scale-title", 1.2) * base_font_pt, 1)
    tokens["font_button"] = round(font.get("scale-button", 1.05) * base_font_pt, 1)
    tokens["font_small"] = round(font.get("scale-small", 0.9) * base_font_pt, 1)

    # Images path (forward slashes for QSS)
    if getattr(sys, "frozen", False):
        images_dir = os.path.join(os.path.dirname(sys.executable), "images")
    else:
        images_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "..", "images"
        )
    tokens["images_dir"] = os.path.normpath(images_dir).replace("\\", "/")

    return template.substitute(tokens)
