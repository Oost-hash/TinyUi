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

"""Platform-aware icon glyphs.

Windows gebruikt Segoe Fluent Icons (systeemfont).
Linux gebruikt Material Symbols Rounded (gebundeld in assets/fonts/).
"""

import logging
import platform as _platform
from pathlib import Path

from PySide6.QtCore import Property, QObject
from PySide6.QtGui import QFontDatabase

_log = logging.getLogger(__name__)

_WINDOWS = _platform.system() == "Windows"

FONT = "Segoe Fluent Icons" if _WINDOWS else "Material Symbols Rounded"

# ── Glyph tabellen ────────────────────────────────────────────────────────────

_SEG: dict[str, str] = {
    # Window controls
    "minimize":     "\uE921",
    "maximize":     "\uE922",
    "restore":      "\uE923",
    "close":        "\uE8BB",
    # Navigatie
    "menu":         "\uE700",
    "menuOpen":     "\uE711",
    "home":         "\uE80F",
    "settings":     "\uE74C",
    # Menu-item iconen
    "settingsAlt":  "\uE713",
    "document":     "\uE8A5",
    "book":         "\uE897",
    "keyboard":     "\uE76E",
    "bugReport":    "\uE730",
    "feedback":     "\uE8F4",
    "group":        "\uE716",
    "updates":      "\uE787",
    "license":      "\uE946",
    "privacy":      "\uE8B6",
}

_MAT: dict[str, str] = {
    # Window controls
    "minimize":     "\uE15B",   # remove (horizontale lijn)
    "maximize":     "\uE3C5",   # crop_square
    "restore":      "\uE3E0",   # filter_none (twee overlappende vierkanten)
    "close":        "\uE5CD",   # close
    # Navigatie
    "menu":         "\uE5D2",   # menu (hamburger)
    "menuOpen":     "\uE5CD",   # close (X — menu-open staat)
    "home":         "\uE88A",   # home
    "settings":     "\uE8B8",   # settings
    # Menu-item iconen
    "settingsAlt":  "\uE8B8",   # settings (zelfde op Linux)
    "document":     "\uE873",   # description
    "book":         "\uE865",   # book
    "keyboard":     "\uE312",   # keyboard
    "bugReport":    "\uE868",   # bug_report
    "feedback":     "\uE87F",   # feedback
    "group":        "\uE7EF",   # group
    "updates":      "\uE923",   # update
    "license":      "\uE90E",   # gavel
    "privacy":      "\uE904",   # privacy_tip
}

_G = _SEG if _WINDOWS else _MAT


# ── Font laden ────────────────────────────────────────────────────────────────

def load_font() -> None:
    """Registreer de gebundelde icon font (alleen nodig op niet-Windows)."""
    if _WINDOWS:
        return
    font_path = Path(__file__).parent / "assets" / "fonts" / "MaterialSymbolsRounded.ttf"
    if font_path.exists():
        fid = QFontDatabase.addApplicationFont(str(font_path))
        if fid < 0:
            _log.warning("Icon font laden mislukt: %s", font_path)
        else:
            _log.debug("Icon font geladen: %s", font_path.name)
    else:
        _log.warning("Icon font niet gevonden: %s", font_path)


# ── QML context object ────────────────────────────────────────────────────────

class Icons(QObject):
    """Exposeert platform-correcte icon glyphs als QML-properties."""

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)

    # Window controls
    @Property(str, constant=True)
    def minimize(self) -> str: return _G["minimize"]

    @Property(str, constant=True)
    def maximize(self) -> str: return _G["maximize"]

    @Property(str, constant=True)
    def restore(self) -> str: return _G["restore"]

    @Property(str, constant=True)
    def close(self) -> str: return _G["close"]

    # Navigatie
    @Property(str, constant=True)
    def menu(self) -> str: return _G["menu"]

    @Property(str, constant=True)
    def menuOpen(self) -> str: return _G["menuOpen"]

    @Property(str, constant=True)
    def home(self) -> str: return _G["home"]

    @Property(str, constant=True)
    def settings(self) -> str: return _G["settings"]

    # Menu-item iconen
    @Property(str, constant=True)
    def settingsAlt(self) -> str: return _G["settingsAlt"]

    @Property(str, constant=True)
    def document(self) -> str: return _G["document"]

    @Property(str, constant=True)
    def book(self) -> str: return _G["book"]

    @Property(str, constant=True)
    def keyboard(self) -> str: return _G["keyboard"]

    @Property(str, constant=True)
    def bugReport(self) -> str: return _G["bugReport"]

    @Property(str, constant=True)
    def feedback(self) -> str: return _G["feedback"]

    @Property(str, constant=True)
    def group(self) -> str: return _G["group"]

    @Property(str, constant=True)
    def updates(self) -> str: return _G["updates"]

    @Property(str, constant=True)
    def license(self) -> str: return _G["license"]

    @Property(str, constant=True)
    def privacy(self) -> str: return _G["privacy"]
