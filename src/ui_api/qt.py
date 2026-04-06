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

"""Qt application and engine factory."""

from __future__ import annotations

import ctypes
import sys
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlEngine

_QML_IMPORT_PATH = Path(__file__).parent.parent  # src/
_APP_ICON_PATH = _QML_IMPORT_PATH / "plugins" / "tinyui" / "assets" / "images" / "logo" / "logo.png"
_APP_USER_MODEL_ID = "OostHash.TinyUi"


def _apply_windows_app_id() -> None:
    """Set an explicit Windows app id so the taskbar groups the app under its own icon."""
    if sys.platform != "win32":
        return
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(_APP_USER_MODEL_ID)


def create_application(argv: list[str] | None = None) -> QApplication:
    if argv is None:
        argv = sys.argv
    _apply_windows_app_id()
    app = QApplication(argv)
    app.setApplicationName("TinyUI")
    if _APP_ICON_PATH.exists():
        app.setWindowIcon(QIcon(str(_APP_ICON_PATH)))
    return app


def create_engine() -> QQmlEngine:
    engine = QQmlEngine()
    engine.addImportPath(str(_QML_IMPORT_PATH))
    return engine
