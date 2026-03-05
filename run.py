#
#  TinyUi - Custom UI layer for TinyPedal
#  Copyright (C) 2025 Oost-hash
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#

"""
TinyUi Launcher - Start TinyPedal core + custom UI
"""

import io
import logging
import os
import sys

# Pad setup voor submodule
sys.path.insert(
    0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "tinypedal")
)

import psutil
from PySide2.QtCore import QCoreApplication, QLocale, Qt
from PySide2.QtGui import QFont, QGuiApplication, QIcon, QPixmapCache
from PySide2.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)
from tinypedal.const_app import APP_NAME, PLATFORM, VERSION
from tinypedal.const_file import ConfigType, ImageFile, LogFile
from tinypedal.log_handler import set_logging_level
from tinypedal.setting import cfg

# TinyPedal imports
from tinypedal import version_check

logger = logging.getLogger("TinyUi")
log_stream = io.StringIO()


def save_pid_file():
    """Save PID info to file"""
    with open(f"{cfg.path.config}tinyui.pid", "w", encoding="utf-8") as f:
        current_pid = os.getpid()
        pid_create_time = psutil.Process(current_pid).create_time()
        f.write(f"{current_pid},{pid_create_time}")


def is_pid_exist() -> bool:
    """Check if already running"""
    try:
        with open(f"{cfg.path.config}tinyui.pid", "r", encoding="utf-8") as f:
            pid_read = f.readline()
        pid = pid_read.split(",")
        pid_last = int(pid[0])
        pid_last_create_time = pid[1]
        if psutil.pid_exists(pid_last):
            if str(psutil.Process(pid_last).create_time()) == pid_last_create_time:
                return True
    except Exception:
        pass
    return False


def single_instance_check():
    """Single instance check"""
    if os.getenv("TINYUI_RESTART") == "TRUE":
        os.environ.pop("TINYUI_RESTART", None)
        save_pid_file()
        return
    if not is_pid_exist():
        save_pid_file()
        return
    QMessageBox.warning(None, "TinyUi", "TinyUi is already running!")
    sys.exit()


def get_version():
    """Get version info"""
    logger.info("TinyUi: 0.1.0")
    logger.info("TinyPedal: %s", VERSION)
    logger.info("Python: %s", version_check.python())
    logger.info("Qt: %s", version_check.qt())


def init_gui() -> QApplication:
    """Initialize Qt Gui (van TinyPedal)"""
    loc = QLocale(QLocale.C)
    loc.setNumberOptions(QLocale.RejectGroupSeparator)
    QLocale.setDefault(loc)

    if cfg.application["enable_high_dpi_scaling"]:
        QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        QGuiApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )

    QApplication.setStyle("Fusion")
    root = QApplication(sys.argv)
    root.setQuitOnLastWindowClosed(
        False
    )  # BELANGRIJK: blijf draaien als hoofdvenster sluit
    root.setApplicationName("TinyUi")
    root.setWindowIcon(QIcon(ImageFile.APP_ICON))

    if not PLATFORM.WINDOWS:
        root.setDesktopFileName("TinyUi-overlay")

    font = root.font()
    if os.getenv("PYSIDE_OVERRIDE") != "6":
        font.setFamily("sans-serif")
    font.setPointSize(10)
    font.setStyleHint(QFont.SansSerif)
    root.setFont(font)
    QPixmapCache.setCacheLimit(0)

    return root


class TinyUiMainWindow(QMainWindow):
    """Jouw custom hoofdvenster - Hello World edition"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("TinyUi - Hello World")
        self.setGeometry(100, 100, 400, 300)

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Hello World label
        label = QLabel(
            "🎉 TinyUi is running!\n\nTinyPedal core + widgets actief op achtergrond"
        )
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: #00ff88;
                background-color: #1a1a1a;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        layout.addWidget(label)

        # Status label
        self.status_label = QLabel("Status: Initializing...")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

    def update_status(self, text):
        self.status_label.setText(f"Status: {text}")


def unset_environment():
    """Clear environment variables"""
    os.environ.pop("QT_QPA_PLATFORM", None)
    os.environ.pop("QT_ENABLE_HIGHDPI_SCALING", None)


def set_environment():
    """Set environment (van TinyPedal)"""
    if PLATFORM.WINDOWS:
        if os.getenv("PYSIDE_OVERRIDE") == "6":
            os.environ["QT_QPA_PLATFORM"] = "windows:darkmode=2:fontengine=freetype"
            os.environ["QT_MEDIA_BACKEND"] = "windows"
        else:
            multimedia_plugin = (
                "windowsmediafoundation"
                if cfg.compatibility["multimedia_plugin_on_windows"] == "WMF"
                else "directshow"
            )
            os.environ["QT_MULTIMEDIA_PREFERRED_PLUGINS"] = multimedia_plugin
    else:
        if cfg.compatibility["enable_x11_platform_plugin_override"]:
            os.environ["QT_QPA_PLATFORM"] = "xcb"

    if not cfg.application["enable_high_dpi_scaling"]:
        os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"


def start_app():
    """Start TinyUi + TinyPedal core"""
    unset_environment()
    set_logging_level(logger, cfg.path.config, "tinyui.log", log_stream, 2)
    get_version()

    # Load TinyPedal config
    cfg.load_global()
    cfg.save(cfg_type=ConfigType.CONFIG)
    cfg.save(cfg_type=ConfigType.SHORTCUTS)

    set_environment()

    # Init GUI
    root = init_gui()
    single_instance_check()

    # Start TinyPedal core modules + widgets (dit start ook zijn tray icon!)
    from tinypedal import loader

    loader.start()

    # Start jouw custom hoofdvenster
    main_window = TinyUiMainWindow()
    main_window.show()
    main_window.update_status("TinyPedal core actief - Tray icon beschikbaar")

    logger.info("TinyUi hoofdvenster gestart")

    # Start event loop
    sys.exit(root.exec_())


if __name__ == "__main__":
    start_app()
