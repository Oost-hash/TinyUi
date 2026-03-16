#  TinyUI - A mod for TinyPedal
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
#  licensed under GPLv3. TinyPedal is included as a submodule.

"""TinyUi bootstrap — tinycore init, Qt init, single instance, start."""

import logging
import os
import sys
from pathlib import Path

import psutil
from PySide6.QtCore import QLocale, Qt
from PySide6.QtGui import QFont, QIcon, QPixmapCache
from PySide6.QtWidgets import QApplication, QMessageBox

from tinycore import create_app
from plugins.demo import DemoPlugin
from tinyui.const import APP_NAME, VERSION

logger = logging.getLogger(APP_NAME)

_ICON_PATH = Path(__file__).parent / "images" / "icon.png"
_PID_FILE = Path.home() / ".tinyui" / "tinyui.pid"


def _resolve_icon() -> str:
    if getattr(sys, "frozen", False):
        return os.path.join(os.path.dirname(sys.executable), "images", "icon.png")
    return str(_ICON_PATH)


def _load_icon() -> QIcon:
    path = _resolve_icon()
    if os.path.exists(path):
        icon = QIcon(path)
        if not icon.isNull():
            return icon
        logger.warning("Icon file exists but failed to load: %s", path)
    logger.warning("No icon found at: %s", path)
    return QIcon()


def _save_pid():
    _PID_FILE.parent.mkdir(parents=True, exist_ok=True)
    pid = os.getpid()
    create_time = psutil.Process(pid).create_time()
    _PID_FILE.write_text(f"{pid},{create_time}", encoding="utf-8")


def _is_already_running() -> bool:
    try:
        line = _PID_FILE.read_text(encoding="utf-8").strip()
        pid_str, create_time_str = line.split(",")
        pid = int(pid_str)
        if psutil.pid_exists(pid):
            if str(psutil.Process(pid).create_time()) == create_time_str:
                return True
    except (OSError, ValueError, psutil.Error):
        pass
    return False


def _init_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    )
    logger.info("=" * 50)
    logger.info("TinyUi v%s starting...", VERSION)


def _init_qt() -> QApplication:
    loc = QLocale(QLocale.c())
    loc.setNumberOptions(QLocale.NumberOption.RejectGroupSeparator)
    QLocale.setDefault(loc)

    QApplication.setStyle("Fusion")
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setApplicationName(APP_NAME)
    app.setWindowIcon(_load_icon())

    font = app.font()
    font.setFamily("sans-serif")
    font.setPointSize(10)
    font.setStyleHint(QFont.StyleHint.SansSerif)
    app.setFont(font)
    QPixmapCache.setCacheLimit(0)

    # Apply theme
    from tinyui.themes.style import load_theme

    app.setStyleSheet(load_theme("dark", font.pointSize()))

    logger.info("Screen DPI: %s", app.devicePixelRatio())
    logger.info("Platform: %s", app.platformName())
    return app


def _check_single_instance() -> bool:
    if os.getenv("TINYUI_RESTART") == "TRUE":
        os.environ.pop("TINYUI_RESTART", None)
        _save_pid()
        return True
    if not _is_already_running():
        _save_pid()
        return True
    return False


def run():
    """Main entry point."""
    _init_logging()

    # --- tinycore boot ---
    if getattr(sys, "frozen", False):
        # Frozen build: config/ next to .exe
        config_dir = Path(sys.executable).parent / "config"
    else:
        # Development: data/plugin-config/ in repo root
        config_dir = Path(__file__).resolve().parents[2] / "data" / "plugin-config"
    core = create_app(config_dir, DemoPlugin())
    core.start()

    # --- Qt ---
    qt_app = _init_qt()

    if not _check_single_instance():
        QMessageBox.warning(None, APP_NAME, "TinyUi is already running!")
        core.stop()
        return 1

    # --- UI ---
    from tinyui.ui.hello_window import HelloWindow

    window = HelloWindow(core)
    window.setWindowIcon(qt_app.windowIcon())
    window.show()

    logger.info("TinyUi ready!")
    exit_code = qt_app.exec()

    core.stop()
    return exit_code


if __name__ == "__main__":
    sys.exit(run())
