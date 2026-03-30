"""Qt application and engine factory."""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlEngine

_QML_IMPORT_PATH = Path(__file__).parent.parent  # src/


def create_application(argv: list[str] | None = None) -> QApplication:
    if argv is None:
        argv = sys.argv
    app = QApplication(argv)
    app.setApplicationName("TinyUI")
    return app


def create_engine() -> QQmlEngine:
    engine = QQmlEngine()
    engine.addImportPath(str(_QML_IMPORT_PATH))
    return engine
