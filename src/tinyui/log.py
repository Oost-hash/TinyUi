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

"""Centrale logging voor tinyui.

Configuratie via TINYUI_DEBUG omgevingsvariabele:

  TINYUI_DEBUG=all           alle debug-categorieën
  TINYUI_DEBUG=menu,state    alleen menu en state
  (niet gezet)               productie-modus — alleen INFO en hoger

Beschikbare categorieën: menu  state  mouse  win32  theme  ui  settings
"""

import logging
import os
import pathlib
import tomllib
from typing import Optional

# Module-niveau configuratie — ingesteld door configure() in main.py
_dev_mode: bool = False
_enabled: frozenset[str] = frozenset()


def _read_pyproject_categories() -> Optional[str]:
    """Lees [tool.tinyui.debug].categories uit pyproject.toml (dev-fallback)."""
    current = pathlib.Path(__file__).resolve().parent
    for _ in range(6):
        candidate = current / "pyproject.toml"
        if candidate.exists():
            with candidate.open("rb") as f:
                data = tomllib.load(f)
            return (
                data.get("tool", {})
                .get("tinyui", {})
                .get("debug", {})
                .get("categories")
            )
        current = current.parent
    return None


def configure() -> None:
    """Bepaal logging-modus via env var of pyproject.toml.

    Prioriteit:
      1. TINYUI_DEBUG env var  (bijv. ``TINYUI_DEBUG=menu,state``)
      2. [tool.tinyui.debug] categories in pyproject.toml
      3. Productie-modus — alleen INFO en hoger

    Roep dit aan vóór alle andere imports in main.py.
    """
    global _dev_mode, _enabled

    raw = os.environ.get("TINYUI_DEBUG") or _read_pyproject_categories() or ""
    cats = {c.strip() for c in raw.split(",") if c.strip()}

    _dev_mode = bool(cats)
    _enabled = frozenset(cats)

    logging.basicConfig(
        level=logging.DEBUG if _dev_mode else logging.INFO,
        format="%(asctime)s %(levelname)-7s  %(name)-42s %(message)s",
        datefmt="%H:%M:%S",
    )


class CategoryLogger:
    """Standaard logger met schakelbare debug-kanalen per categorie."""

    __slots__ = ("_log",)

    def __init__(self, name: str) -> None:
        self._log = logging.getLogger(name)

    def _cat(self, category: str, msg: str, **kwargs) -> None:
        if not (_dev_mode and self._log.isEnabledFor(logging.DEBUG)):
            return
        if "all" not in _enabled and category not in _enabled:
            return
        detail = "  ".join(f"{k}={v!r}" for k, v in kwargs.items())
        self._log.debug("[%-5s] %s  %s", category, msg, detail)

    # ── Debug-kanalen ──────────────────────────────────────────────────────
    def menu(self, msg: str, **kw) -> None:
        self._cat("menu", msg, **kw)

    def state(self, msg: str, **kw) -> None:
        self._cat("state", msg, **kw)

    def mouse(self, msg: str, **kw) -> None:
        self._cat("mouse", msg, **kw)

    def win32(self, msg: str, **kw) -> None:
        self._cat("win32", msg, **kw)

    def theme(self, msg: str, **kw) -> None:
        self._cat("theme", msg, **kw)

    def ui(self, msg: str, **kw) -> None:
        self._cat("ui", msg, **kw)

    def settings(self, msg: str, **kw) -> None:
        self._cat("settings", msg, **kw)

    # ── Standaard niveaus (altijd actief) ──────────────────────────────────
    def info(self, msg, *a, **kw):
        self._log.info(msg, *a, **kw)

    def warning(self, msg, *a, **kw):
        self._log.warning(msg, *a, **kw)

    def error(self, msg, *a, **kw):
        self._log.error(msg, *a, **kw)

    def exception(self, msg, *a, **kw):
        self._log.exception(msg, *a, **kw)


def get_logger(name: str) -> CategoryLogger:
    """Geeft een CategoryLogger terug voor de gegeven module-naam."""
    return CategoryLogger(name)
