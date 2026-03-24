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

Configuration via [tool.tinyui.debug] in pyproject.toml or TINYUI_DEBUG env var:

  categories    = "all"       enable all debug categories
  categories    = "widget"    only the widget channel
  (unset)                     no debug output; INFO+ only

  console_level = "INFO"      attach a terminal StreamHandler at this level.
                  "WARNING"   Set to the level you want in PowerShell/bash.
                  "DEBUG"     Omit entirely to suppress terminal output.

The terminal (console_level) and the in-app Dev Tools console are independent:
Dev Tools always captures everything the root logger passes through.

Available categories:
  connector  menu  mouse  overlay  settings  ui  widget
"""

import logging
import os
import pathlib
import tomllib

# All known debug categories, in alphabetical order.
ALL_CATEGORIES: tuple[str, ...] = (
    "connector", "menu", "mouse", "overlay", "settings", "ui", "widget",
)

# Module-level configuration — set by configure() in main.py
_dev_mode: bool = False
_enabled: set[str] = set()


def _read_pyproject_debug() -> dict:
    """Read the [tool.tinyui.debug] table from the nearest pyproject.toml."""
    current = pathlib.Path(__file__).resolve().parent
    for _ in range(6):
        candidate = current / "pyproject.toml"
        if candidate.exists():
            with candidate.open("rb") as f:
                data = tomllib.load(f)
            return data.get("tool", {}).get("tinyui", {}).get("debug", {})
        current = current.parent
    return {}


_LEVEL_MAP: dict[str, int] = {
    "DEBUG":   logging.DEBUG,
    "INFO":    logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR":   logging.ERROR,
}


def configure() -> None:
    """Determine logging mode from env var or pyproject.toml and wire up handlers.

    ``console_level`` in [tool.tinyui.debug] controls the terminal
    StreamHandler independently of the in-app Dev Tools console.
    Omit it to keep the terminal silent.

    Call this before all other imports in main.py.
    """
    global _dev_mode, _enabled

    cfg = _read_pyproject_debug()

    raw = os.environ.get("TINYUI_DEBUG") or cfg.get("categories", "") or ""
    cats = {c.strip() for c in raw.split(",") if c.strip()}

    _dev_mode = bool(cats)
    _enabled  = set(cats)

    # Root level: DEBUG in dev mode so category-gated records can propagate.
    root = logging.getLogger()
    root.setLevel(logging.DEBUG if _dev_mode else logging.INFO)

    # Terminal StreamHandler — only added when console_level is set.
    # Omitting console_level suppresses all terminal output.
    # The in-app QtLogHandler (added by LogViewModel) is independent and
    # always captures at DEBUG so Dev Tools sees everything.
    raw_level = str(cfg.get("console_level", "")).upper()
    if raw_level in _LEVEL_MAP and not root.handlers:
        handler = logging.StreamHandler()
        handler.setLevel(_LEVEL_MAP[raw_level])
        handler.setFormatter(logging.Formatter(
            fmt="%(asctime)s %(levelname)-7s  %(name)-42s %(message)s",
            datefmt="%H:%M:%S",
        ))
        root.addHandler(handler)


def get_dev_mode() -> bool:
    """Return True when debug-channel output is currently active."""
    return _dev_mode


def set_dev_mode(enabled: bool) -> None:
    """Enable or disable all debug-channel output at runtime.

    Also updates the root-logger level so DEBUG records actually propagate.
    When enabling from a cold start (no categories configured), all categories
    are activated automatically so the user sees output immediately.
    """
    global _dev_mode, _enabled
    _dev_mode = enabled
    if enabled and not _enabled:
        _enabled = set(ALL_CATEGORIES)
    logging.getLogger().setLevel(logging.DEBUG if enabled else logging.INFO)


def get_category_states() -> list[tuple[str, bool]]:
    """Return (name, enabled) for every known category, in alphabetical order."""
    all_on = "all" in _enabled
    return [(cat, all_on or cat in _enabled) for cat in ALL_CATEGORIES]


def set_category_enabled(cat: str, enabled: bool) -> None:
    """Enable or disable a single debug category at runtime.

    If the magic token ``"all"`` was active, it is expanded to individual
    entries first so subsequent per-category toggles work correctly.
    """
    global _enabled
    if "all" in _enabled:
        _enabled = set(ALL_CATEGORIES)
        _enabled.discard("all")
    if enabled:
        _enabled.add(cat)
    else:
        _enabled.discard(cat)


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
    def connector(self, msg: str, **kw) -> None:
        self._cat("connector", msg, **kw)

    def menu(self, msg: str, **kw) -> None:
        self._cat("menu", msg, **kw)

    def mouse(self, msg: str, **kw) -> None:
        self._cat("mouse", msg, **kw)

    def overlay(self, msg: str, **kw) -> None:
        self._cat("overlay", msg, **kw)

    def settings(self, msg: str, **kw) -> None:
        self._cat("settings", msg, **kw)

    def ui(self, msg: str, **kw) -> None:
        self._cat("ui", msg, **kw)

    def widget(self, msg: str, **kw) -> None:
        self._cat("widget", msg, **kw)

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
