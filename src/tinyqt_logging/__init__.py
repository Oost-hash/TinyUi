"""Host/bootstrap logging setup for TinyQt applications."""

from tinyqt_logging.app_logger import (
    AppLogger,
    configure_app_logger,
    get_app_logger,
    read_app_logging_config,
)


def configure() -> None:
    """Configure app logging first, then optional diagnostics wiring."""
    from tinyruntime_schema.logging import configure_diagnostics

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
