"""Host/bootstrap logging setup for TinyQt applications."""

from tinyqt_logging.app_logger import (
    AppLogger,
    configure_app_logger,
    get_app_logger,
    read_app_logging_config,
)
from tinyruntime_schema.logging import configure_diagnostics


def configure() -> None:
    """Configure app logging first, then optional diagnostics wiring."""
    config = read_app_logging_config()
    console_level = str(config.get("console_level", "") or "")
    configure_app_logger(console_level)
    configure_diagnostics()


__all__ = [
    "AppLogger",
    "configure",
    "configure_app_logger",
    "get_app_logger",
    "read_app_logging_config",
]
