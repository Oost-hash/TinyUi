"""Logging boundary between product runtime output and optional diagnostics."""

from .core import ProductLogger, configure_root_logger, get_product_logger, read_logging_config
from .diagnostics import (
    ALL_CATEGORIES,
    DiagnosticsLogger,
    configure_diagnostics,
    diagnostics_enabled,
    get_category_states,
    get_dev_mode,
    get_logger,
    set_category_enabled,
    set_dev_mode,
)


def configure() -> None:
    """Configure product logging first, then opt into diagnostics if requested."""
    config = read_logging_config()
    console_level = str(config.get("console_level", "") or "")
    configure_root_logger(console_level)
    configure_diagnostics()


__all__ = [
    "ALL_CATEGORIES",
    "DiagnosticsLogger",
    "ProductLogger",
    "configure",
    "configure_diagnostics",
    "configure_root_logger",
    "diagnostics_enabled",
    "get_category_states",
    "get_dev_mode",
    "get_logger",
    "get_product_logger",
    "read_logging_config",
    "set_category_enabled",
    "set_dev_mode",
]
