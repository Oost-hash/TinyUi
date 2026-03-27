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

"""Logging boundary between app runtime output and optional diagnostics."""

from tinycore.diagnostics.log_categories import (
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
from tinycore.diagnostics.log_records import LogInspector, LogRecordEntry

from .app_logger import AppLogger, configure_app_logger, get_app_logger, read_app_logging_config


def configure() -> None:
    """Configure app logging first, then opt into diagnostics if requested."""
    config = read_app_logging_config()
    console_level = str(config.get("console_level", "") or "")
    configure_app_logger(console_level)
    configure_diagnostics()


__all__ = [
    "ALL_CATEGORIES",
    "DiagnosticsLogger",
    "LogInspector",
    "LogRecordEntry",
    "AppLogger",
    "configure",
    "configure_app_logger",
    "configure_diagnostics",
    "diagnostics_enabled",
    "get_category_states",
    "get_dev_mode",
    "get_app_logger",
    "get_logger",
    "read_app_logging_config",
    "set_category_enabled",
    "set_dev_mode",
]
