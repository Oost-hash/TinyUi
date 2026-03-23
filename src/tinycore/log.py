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

"""Central logging — shared across tinycore, tinywidgets, tinyui.

Configuration via TINYUI_DEBUG environment variable:

  TINYUI_DEBUG=all              all debug categories
  TINYUI_DEBUG=widget,overlay   widget and overlay only
  (unset)                   production mode — INFO and above only

Available categories:
  menu  state  mouse  win32  theme  ui  settings
  connector  connector_polling  widget  overlay
"""

import logging
import os
import pathlib
import tomllib
from typing import Optional

# Module-level configuration — set by configure() in main.py
_dev_mode: bool = False
_enabled: frozenset[str] = frozenset()


def _read_pyproject_categories() -> Optional[str]:
    """Read [tool.tinyui.debug].categories from pyproject.toml (dev fallback)."""
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
    """Determine logging mode via env var or pyproject.toml.

    Priority:
      1. TINYUI_DEBUG env var  (e.g. ``TINYUI_DEBUG=menu,state``)
      2. [tool.tinyui.debug] categories in pyproject.toml
      3. Production mode — INFO and above only

    Call this before all other imports in main.py.
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
    """Standard logger with switchable debug channels per category."""

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

    # ── Debug channels ─────────────────────────────────────────────────────
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

    def connector(self, msg: str, **kw) -> None:
        self._cat("connector", msg, **kw)

    def connector_polling(self, msg: str, **kw) -> None:
        self._cat("connector_polling", msg, **kw)

    def widget(self, msg: str, **kw) -> None:
        self._cat("widget", msg, **kw)

    def overlay(self, msg: str, **kw) -> None:
        self._cat("overlay", msg, **kw)

    # ── Standard levels (always active) ───────────────────────────────────
    def info(self, msg, *a, **kw):
        self._log.info(msg, *a, **kw)

    def warning(self, msg, *a, **kw):
        self._log.warning(msg, *a, **kw)

    def error(self, msg, *a, **kw):
        self._log.error(msg, *a, **kw)

    def exception(self, msg, *a, **kw):
        self._log.exception(msg, *a, **kw)


def get_logger(name: str) -> CategoryLogger:
    """Returns a CategoryLogger for the given module name."""
    return CategoryLogger(name)
