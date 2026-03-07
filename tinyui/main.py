#
#  TinyUi - Application Entry Point
#  Copyright (C) 2025 Oost-hash
#

"""TinyUi bootstrap — config, logging, Qt init, single instance, start."""

import io
import logging
import os
import sys

import psutil
from PySide2.QtCore import QCoreApplication, QLocale, Qt
from PySide2.QtGui import QFont, QGuiApplication, QIcon, QPixmapCache
from PySide2.QtWidgets import QApplication, QMessageBox, QSystemTrayIcon

from tinyui.backend.constants import TP_VERSION, ConfigType, ImageFile
from tinyui.backend.core_loader import core
from tinyui.backend.misc import set_environment, set_logging_level, unset_environment
from tinyui.backend.settings import cfg
from tinyui.version import __version__ as TINYUI_VERSION

logger = logging.getLogger("TinyUi")

# TinyUi icon path (relative to tinyui package)
_TINYUI_ICON = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images", "icon.png")


def _tinyui_icon() -> str:
    """Resolve TinyUi icon path, works both frozen and development."""
    if getattr(sys, "frozen", False):
        return os.path.join(os.path.dirname(sys.executable), "tinyui", "images", "icon.png")
    return _TINYUI_ICON


def _app_root():
    """Application root path (works frozen and dev)."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tinypedal"
    )


def _load_icon() -> QIcon:
    """Load TinyUi icon with TinyPedal fallback."""
    path = _tinyui_icon()
    if os.path.exists(path):
        return QIcon(path)
    logger.warning(f"TinyUi icon not found: {path}")
    tp_path = os.path.join(_app_root(), ImageFile.APP_ICON)
    if os.path.exists(tp_path):
        return QIcon(tp_path)
    return QIcon()


# --- PID helpers for single instance check ---

def _save_pid_file():
    with open(f"{cfg.path.config}tinyui.pid", "w", encoding="utf-8") as f:
        pid = os.getpid()
        create_time = psutil.Process(pid).create_time()
        f.write(f"{pid},{create_time}")


def _is_pid_exist() -> bool:
    try:
        with open(f"{cfg.path.config}tinyui.pid", "r", encoding="utf-8") as f:
            line = f.readline().strip()
        pid_str, create_time_str = line.split(",")
        pid = int(pid_str)
        if psutil.pid_exists(pid):
            if str(psutil.Process(pid).create_time()) == create_time_str:
                return True
    except (OSError, ValueError, psutil.Error) as exc:
        logger.debug("PID check failed: %s", exc)
    return False


# --- Bootstrap helpers ---

def _init_config():
    """Load global config and save defaults."""
    unset_environment()
    cfg.load_global()
    cfg.save(cfg_type=ConfigType.CONFIG)
    cfg.save(cfg_type=ConfigType.SHORTCUTS)


def _init_logging():
    """Setup logging to file and stream."""
    log_stream = io.StringIO()
    set_logging_level(logger, cfg.path.config, "tinyui.log", log_stream, 2)
    logger.info("=" * 50)
    logger.info(f"TinyUi v{TINYUI_VERSION} Starting...")
    set_environment()


def _init_qt() -> QApplication:
    """Create and configure the Qt application."""
    loc = QLocale(QLocale.C)
    loc.setNumberOptions(QLocale.RejectGroupSeparator)
    QLocale.setDefault(loc)

    if cfg.application["enable_high_dpi_scaling"]:
        QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        QGuiApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )

    QApplication.setStyle("Fusion")
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setApplicationName("TinyUi")
    app.setWindowIcon(_load_icon())

    font = app.font()
    if os.getenv("PYSIDE_OVERRIDE") != "6":
        font.setFamily("sans-serif")
    font.setPointSize(10)
    font.setStyleHint(QFont.SansSerif)
    app.setFont(font)
    QPixmapCache.setCacheLimit(0)

    logger.info(f"Screen DPI: {app.devicePixelRatio()}")
    logger.info(f"Platform: {app.platformName()}")
    return app


def _check_single_instance() -> bool:
    """Returns True if this is the only instance, False if already running."""
    if os.getenv("TINYUI_RESTART") == "TRUE":
        os.environ.pop("TINYUI_RESTART", None)
        _save_pid_file()
        return True
    if not _is_pid_exist():
        _save_pid_file()
        return True
    return False


# --- Entry point ---

def run():
    """Main entry point."""
    from tinyui.ui.main_window import MainWindow

    _init_config()
    _init_logging()
    app = _init_qt()

    if not _check_single_instance():
        QMessageBox.warning(None, "TinyUi", "TinyUi is already running!")
        return 1

    core.start()
    logger.info(f"TinyPedal: {TP_VERSION}")

    # Setup tray icon (app-level, independent of window)
    from tinyui.ui.menu import OverlayMenu

    icon = _load_icon()
    tray_icon = QSystemTrayIcon()
    tray_icon.setIcon(icon)

    window = MainWindow(tray_icon=tray_icon)

    tray_icon.setToolTip(window.windowTitle())
    tray_icon.activated.connect(
        lambda reason: window.show_app()
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick
        else None
    )
    tray_icon.setContextMenu(OverlayMenu("Overlay", window, True))
    tray_icon.show()

    window.show()

    logger.info("TinyUi ready!")
    return app.exec_()
