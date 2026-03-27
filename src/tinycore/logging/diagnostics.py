"""Optional diagnostics logging layered on top of product logging."""

from __future__ import annotations

import logging
import os

from .core import ProductLogger, get_product_logger, read_logging_config


ALL_CATEGORIES: tuple[str, ...] = (
    "connector",
    "menu",
    "mouse",
    "overlay",
    "settings",
    "ui",
    "widget",
)

_dev_mode = False
_enabled: set[str] = set()


def configure_diagnostics() -> None:
    """Apply optional diagnostics config without redefining product logging."""
    global _dev_mode, _enabled

    cfg = read_logging_config()
    raw = os.environ.get("TINYUI_DEBUG") or str(cfg.get("categories", "") or "")
    categories = {value.strip() for value in raw.split(",") if value.strip()}

    _enabled = set(categories)
    _dev_mode = bool(categories)

    if _dev_mode:
        logging.getLogger().setLevel(logging.DEBUG)


def diagnostics_enabled() -> bool:
    """Return True when optional diagnostics are active."""
    return _dev_mode


def get_dev_mode() -> bool:
    """Compatibility helper for the existing Dev Tools settings VM."""
    return _dev_mode


def set_dev_mode(enabled: bool) -> None:
    """Enable or disable all diagnostics categories."""
    global _dev_mode, _enabled
    _dev_mode = enabled
    _enabled = set(ALL_CATEGORIES) if enabled else set()
    logging.getLogger().setLevel(logging.DEBUG if enabled else logging.INFO)


def get_category_states() -> list[tuple[str, bool]]:
    """Return enabled state for all known diagnostics categories."""
    all_on = "all" in _enabled
    return [(category, all_on or category in _enabled) for category in ALL_CATEGORIES]


def set_category_enabled(category: str, enabled: bool) -> None:
    """Toggle one diagnostics category."""
    global _dev_mode, _enabled
    if "all" in _enabled:
        _enabled = set(ALL_CATEGORIES)
        _enabled.discard("all")
    if enabled:
        _enabled.add(category)
    else:
        _enabled.discard(category)
    _dev_mode = bool(_enabled)
    logging.getLogger().setLevel(logging.DEBUG if _dev_mode else logging.INFO)


class DiagnosticsLogger(ProductLogger):
    """Product logger plus category-gated diagnostics helpers."""

    def _category(self, category: str, msg: str, **kwargs: object) -> None:
        if not (_dev_mode and self._log.isEnabledFor(logging.DEBUG)):
            return
        if "all" not in _enabled and category not in _enabled:
            return
        detail = "  ".join(f"{key}={value!r}" for key, value in kwargs.items())
        if detail:
            self._log.debug("[%-9s] %s  %s", category, msg, detail)
            return
        self._log.debug("[%-9s] %s", category, msg)

    def connector(self, msg: str, **kwargs: object) -> None:
        self._category("connector", msg, **kwargs)

    def menu(self, msg: str, **kwargs: object) -> None:
        self._category("menu", msg, **kwargs)

    def mouse(self, msg: str, **kwargs: object) -> None:
        self._category("mouse", msg, **kwargs)

    def overlay(self, msg: str, **kwargs: object) -> None:
        self._category("overlay", msg, **kwargs)

    def settings(self, msg: str, **kwargs: object) -> None:
        self._category("settings", msg, **kwargs)

    def ui(self, msg: str, **kwargs: object) -> None:
        self._category("ui", msg, **kwargs)

    def widget(self, msg: str, **kwargs: object) -> None:
        self._category("widget", msg, **kwargs)

    def startup_phase(self, phase: str, elapsed_ms: float, **extra: object) -> None:
        """Emit startup timings only while diagnostics are enabled."""
        if not _dev_mode:
            return
        fields = " ".join(f"{key}={value}" for key, value in extra.items())
        suffix = f" {fields}" if fields else ""
        self.info("startup phase=%s ms=%.1f%s", phase, elapsed_ms, suffix)


def get_logger(name: str) -> DiagnosticsLogger:
    """Return the shared diagnostics-capable logger wrapper."""
    return DiagnosticsLogger(get_product_logger(name)._log)
