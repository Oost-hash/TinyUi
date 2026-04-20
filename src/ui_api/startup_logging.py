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

"""Minimal startup diagnostics for packaged and source launches."""

from __future__ import annotations

import logging
import os
import sys
from types import TracebackType
from pathlib import Path
from typing import Any

_LOGGER_NAME = "tinyui.startup"
_LOG_FILE_NAME = "startup.log"
_APP_DIR_NAME = "TinyUi"
_logger = logging.getLogger(_LOGGER_NAME)
_configured_path: Path | None = None
_qt_handler_installed = False
_excepthook_installed = False


def configure_startup_logging(logs_dir: Path | None = None) -> Path:
    """Ensure startup diagnostics are written to a stable file."""

    global _configured_path

    if logs_dir is None:
        logs_dir = _default_logs_dir()
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_path = logs_dir / _LOG_FILE_NAME

    if _configured_path == log_path:
        return log_path

    for handler in list(_logger.handlers):
        _logger.removeHandler(handler)
        handler.close()

    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    )
    _logger.addHandler(file_handler)
    _logger.setLevel(logging.INFO)
    _logger.propagate = False
    _configured_path = log_path
    _logger.info("startup logging configured")
    return log_path


def install_startup_diagnostics(logs_dir: Path | None = None) -> Path:
    """Configure file logging and process-level diagnostic hooks."""

    log_path = configure_startup_logging(logs_dir)
    _install_excepthook()
    return log_path


def install_qt_message_logging(logs_dir: Path | None = None) -> Path:
    """Capture Qt and QML runtime messages in the startup log."""

    global _qt_handler_installed

    log_path = configure_startup_logging(logs_dir)
    if _qt_handler_installed:
        return log_path

    from PySide6.QtCore import QtMsgType, qInstallMessageHandler

    def _qt_message_handler(
        mode: QtMsgType,
        context: Any,
        message: str,
    ) -> None:
        levels = {
            QtMsgType.QtDebugMsg: logging.DEBUG,
            QtMsgType.QtInfoMsg: logging.INFO,
            QtMsgType.QtWarningMsg: logging.WARNING,
            QtMsgType.QtCriticalMsg: logging.ERROR,
            QtMsgType.QtFatalMsg: logging.CRITICAL,
        }
        file_name = getattr(context, "file", "") or "unknown"
        line = getattr(context, "line", 0) or 0
        category = getattr(context, "category", "") or "qt"
        _logger.log(
            levels.get(mode, logging.INFO),
            "qt[%s] %s:%s %s",
            category,
            file_name,
            line,
            message,
        )

    qInstallMessageHandler(_qt_message_handler)
    _qt_handler_installed = True
    _logger.info("Qt message logging installed")
    return log_path


def log_startup_step(message: str, *, level: int = logging.INFO, exc_info: bool = False) -> None:
    """Write one startup diagnostic line."""

    configure_startup_logging()
    _logger.log(level, message, exc_info=exc_info)


def startup_log_path() -> Path:
    """Return the active startup log path."""

    return configure_startup_logging()


def _install_excepthook() -> None:
    """Capture uncaught Python exceptions during startup."""

    global _excepthook_installed

    if _excepthook_installed:
        return

    previous_hook = sys.excepthook

    def _logging_excepthook(
        exc_type: type[BaseException],
        exc_value: BaseException,
        exc_traceback: TracebackType | None,
    ) -> None:
        _logger.critical(
            "uncaught exception during startup",
            exc_info=(exc_type, exc_value, exc_traceback),
        )
        previous_hook(exc_type, exc_value, exc_traceback)

    sys.excepthook = _logging_excepthook
    _excepthook_installed = True


def _default_logs_dir() -> Path:
    """Resolve the user-level log directory before persistence is available."""

    if sys.platform == "win32":
        base_dir = Path(os.getenv("APPDATA", str(Path.home())))
    else:
        base_dir = Path(os.getenv("XDG_CONFIG_HOME", str(Path.home() / ".config")))
    return base_dir / _APP_DIR_NAME / "logs"
