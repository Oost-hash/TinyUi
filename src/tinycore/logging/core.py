"""Product logging primitives used by the shipped app runtime."""

from __future__ import annotations

import logging
import pathlib
import tomllib
from dataclasses import dataclass
from typing import Any


_LEVEL_MAP: dict[str, int] = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
}


def read_logging_config() -> dict[str, object]:
    """Read the nearest TinyUi debug config from pyproject.toml."""
    current = pathlib.Path(__file__).resolve().parent
    for _ in range(7):
        candidate = current / "pyproject.toml"
        if candidate.exists():
            with candidate.open("rb") as file_obj:
                data = tomllib.load(file_obj)
            debug_cfg = data.get("tool", {}).get("tinyui", {}).get("debug", {})
            if isinstance(debug_cfg, dict):
                return debug_cfg
            return {}
        current = current.parent
    return {}


def configure_root_logger(console_level: str | None) -> logging.Logger:
    """Configure root logging for product-safe runtime output."""
    root = logging.getLogger()
    root.setLevel(logging.INFO)

    normalized = (console_level or "").upper()
    if normalized in _LEVEL_MAP and not root.handlers:
        handler = logging.StreamHandler()
        handler.setLevel(_LEVEL_MAP[normalized])
        handler.setFormatter(
            logging.Formatter(
                fmt="%(asctime)s %(levelname)-7s  %(name)-42s %(message)s",
                datefmt="%H:%M:%S",
            )
        )
        root.addHandler(handler)

    return root


@dataclass(frozen=True)
class ProductLogger:
    """Minimal logger surface intended for product runtime usage."""

    _log: logging.Logger

    def info(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self._log.info(msg, *args, **kwargs)

    def warning(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self._log.warning(msg, *args, **kwargs)

    def error(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self._log.error(msg, *args, **kwargs)

    def exception(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self._log.exception(msg, *args, **kwargs)


def get_product_logger(name: str) -> ProductLogger:
    """Return the product logger for one module."""
    return ProductLogger(logging.getLogger(name))
