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

import os
import platform as _platform
import tomllib

from PySide6.QtCore import QObject, Property, Signal
from PySide6.QtQml import QmlElement

QML_IMPORT_NAME = "TinyUI"
QML_IMPORT_MAJOR_VERSION = 1

_sys = _platform.system()
_FONT_FAMILY = (
    "Segoe UI"           if _sys == "Windows" else
    ".AppleSystemUIFont" if _sys == "Darwin"  else
    ""                   # Qt system default op Linux
)


def _load_toml(name: str) -> dict:
    themes_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "themes")
    path = os.path.join(themes_dir, f"{name.lower()}.toml")
    with open(path, "rb") as f:
        return tomllib.load(f)


@QmlElement
class Theme(QObject):
    """Laadt kleuren uit TOML en exposeert ze als QML-bindbare properties."""

    changed = Signal()

    def __init__(self, name: str = "dark", base_font_pt: int = 13):
        super().__init__()
        self._base = base_font_pt
        self._colors = {}
        self._font = {}
        self.load(name)

    def load(self, name: str):
        data = _load_toml(name)
        self._colors = data.get("colors", {})
        self._font = data.get("font", {})
        self.changed.emit()

    def _c(self, key: str) -> str:
        return self._colors.get(key, "#ff00ff")  # magenta als token ontbreekt

    def _font_size(self, scale_key: str) -> int:
        return round(self._font.get(scale_key, 1.0) * self._base)

    # ── Window chrome (static) ────────────────────────────────────────────

    @Property(int, constant=True)
    def titleBarHeight(self): return 36

    @Property(int, constant=True)
    def resizeBorder(self): return 8

    @Property(int, constant=True)
    def resizeCorner(self): return 20

    @Property(int, constant=True)
    def leftButtonWidth(self): return 300

    @Property(int, constant=True)
    def rightButtonWidth(self): return 142

    @Property(int, constant=True)
    def fontSizeBase(self): return self._base

    @Property(str, constant=True)
    def fontFamily(self): return _FONT_FAMILY

    # ── Font sizes (uit TOML schalen) ────────────────────────────────────

    @Property(int, notify=changed)
    def fontSizeTitle(self): return self._font_size("scale-title")

    @Property(int, notify=changed)
    def fontSizeSmall(self): return self._font_size("scale-small")

    # ── Kleuren ──────────────────────────────────────────────────────────

    @Property(str, notify=changed)
    def surface(self): return self._c("surface")

    @Property(str, notify=changed)
    def surfaceAlt(self): return self._c("surface-alt")

    @Property(str, notify=changed)
    def surfaceRaised(self): return self._c("surface-raised")

    @Property(str, notify=changed)
    def surfaceFloating(self): return self._c("surface-floating")

    @Property(str, notify=changed)
    def border(self): return self._c("border")

    @Property(str, notify=changed)
    def text(self): return self._c("text")

    @Property(str, notify=changed)
    def textSecondary(self): return self._c("text-secondary")

    @Property(str, notify=changed)
    def textMuted(self): return self._c("text-muted")

    @Property(str, notify=changed)
    def accent(self): return self._c("accent")

    @Property(str, notify=changed)
    def accentHover(self): return self._c("accent-hover")

    @Property(str, notify=changed)
    def accentPressed(self): return self._c("accent-pressed")

    @Property(str, notify=changed)
    def accentText(self): return self._c("accent-text")

    @Property(str, notify=changed)
    def success(self): return self._c("success")

    @Property(str, notify=changed)
    def warning(self): return self._c("warning")

    @Property(str, notify=changed)
    def danger(self): return self._c("danger")

    @Property(str, notify=changed)
    def info(self): return self._c("info")
