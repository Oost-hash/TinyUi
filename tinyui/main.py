#
#  TinyUi - Main Window
#  Copyright (C) 2025 Oost-hash
#

"""TinyUi main window and application entry point."""

import io
import logging
import os
import sys

import psutil
from PySide2.QtCore import QCoreApplication, QLocale, Qt, Slot
from PySide2.QtGui import QFont, QGuiApplication, QIcon, QPixmapCache
from PySide2.QtWidgets import (
    QApplication,
    QMainWindow,
    QMessageBox,
    QSystemTrayIcon,
)

from tinyui.backend.constants import TP_APP_NAME, TP_VERSION, ConfigType, ImageFile
from tinyui.backend.controls import app_signal
from tinyui.backend.misc import set_environment, set_logging_level, unset_environment
from tinyui.backend.settings import cfg
from tinyui.version import __version__ as TINYUI_VERSION

from tinyui.backend.core_loader import core
from .ui import set_style_palette, set_style_window
from .ui._common import DialogSingleton, UIScaler
from .ui.app import StatusButtonBar, TabView
from .ui.menu import (
    APIMenu,
    ConfigMenu,
    HelpMenu,
    OverlayMenu,
    ToolsMenu,
    WindowMenu,
)

logger = logging.getLogger("TinyUi")

# TinyUi icon path (relative to tinyui package)
_TINYUI_ICON = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images", "icon.png")


def _tinyui_icon() -> str:
    """Resolve TinyUi icon path, works both frozen and development."""
    if getattr(sys, "frozen", False):
        return os.path.join(os.path.dirname(sys.executable), "tinyui", "images", "icon.png")
    return _TINYUI_ICON


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


def _app_root():
    """Application root path (works frozen and dev)."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tinypedal"
    )


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


# --- MainWindow ---

class MainWindow(QMainWindow):
    """TinyUi main window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"TinyUi v{TINYUI_VERSION} | {TP_APP_NAME} v{TP_VERSION}")
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        self._last_style = None
        self._tray_icon = None

        self._setup_statusbar()
        self._setup_menubar()
        self._setup_tabs()
        self._setup_tray()
        self._setup_window_state()
        self._connect_signals()

        app_signal.refresh.emit(True)

    def _setup_statusbar(self):
        self.setStatusBar(StatusButtonBar(self))

    def _setup_menubar(self):
        logger.info("Loading menu bar...")
        menu = self.menuBar()
        menu.addMenu(OverlayMenu("Overlay", self))

        menu_api = APIMenu("API", self)
        menu.addMenu(menu_api)
        self.statusBar().button_api.setMenu(menu_api)

        menu.addMenu(ConfigMenu("Config", self))
        menu.addMenu(ToolsMenu("Tools", self))
        menu.addMenu(WindowMenu("Window", self))
        menu.addMenu(HelpMenu("Help", self))

    def _setup_tabs(self):
        self.tab_view = TabView(self)
        self.setCentralWidget(self.tab_view)

    def _setup_tray(self):
        logger.info("Loading tray icon...")
        tray_icon = QSystemTrayIcon(self)
        tray_icon.setIcon(_load_icon())
        tray_icon.setToolTip(self.windowTitle())
        tray_icon.activated.connect(self._tray_activated)

        tray_menu = OverlayMenu("Overlay", self, True)
        tray_icon.setContextMenu(tray_menu)
        tray_icon.show()
        self._tray_icon = tray_icon

    def _tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.showNormal()
            self.activateWindow()

    def _setup_window_state(self):
        self.setMinimumSize(UIScaler.size(23), UIScaler.size(36))
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, False)

        if cfg.application["remember_size"]:
            self.resize(
                cfg.application["window_width"],
                cfg.application["window_height"],
            )

        if cfg.application["remember_position"]:
            self._load_window_position()

        if cfg.compatibility["enable_window_position_correction"]:
            self._verify_window_position()

        if cfg.application["show_at_startup"]:
            self.showNormal()
        elif not cfg.application["minimize_to_tray"]:
            self.showMinimized()

    def _load_window_position(self):
        app_pos_x = cfg.application["position_x"]
        app_pos_y = cfg.application["position_y"]
        if 0 == app_pos_x == app_pos_y:
            self._save_window_state()
        else:
            self.move(app_pos_x, app_pos_y)

    def _verify_window_position(self):
        screen_geo = self.screen().geometry()
        app_pos_x = min(
            max(self.x(), screen_geo.left()),
            screen_geo.right() - self.minimumWidth(),
        )
        app_pos_y = min(
            max(self.y(), screen_geo.top()),
            screen_geo.bottom() - self.minimumHeight(),
        )
        if self.x() != app_pos_x or self.y() != app_pos_y:
            self.move(app_pos_x, app_pos_y)

    def _save_window_state(self):
        save_changes = False

        if cfg.application["remember_position"]:
            last_pos = (
                cfg.application["position_x"],
                cfg.application["position_y"],
            )
            new_pos = self.x(), self.y()
            if last_pos != new_pos:
                cfg.application["position_x"] = new_pos[0]
                cfg.application["position_y"] = new_pos[1]
                save_changes = True

        if cfg.application["remember_size"]:
            last_size = (
                cfg.application["window_width"],
                cfg.application["window_height"],
            )
            new_size = self.width(), self.height()
            if last_size != new_size:
                cfg.application["window_width"] = new_size[0]
                cfg.application["window_height"] = new_size[1]
                save_changes = True

        if save_changes:
            cfg.save(0, cfg_type=ConfigType.CONFIG)

    def _connect_signals(self):
        app_signal.refresh.connect(self._on_refresh)
        app_signal.quitapp.connect(self.quit_app)
        app_signal.reload.connect(self.reload_preset)

    @Slot(bool)
    def _on_refresh(self):
        style = cfg.application["window_color_theme"]
        if self._last_style != style:
            self._last_style = style
            set_style_palette(style)
            self.setStyleSheet(set_style_window(QApplication.font().pointSize()))
            logger.info(f"Theme loaded: {style}")

    @Slot(bool)
    def reload_preset(self, check_singleton: bool = True):
        if check_singleton and DialogSingleton.is_opened(ConfigType.CONFIG):
            QMessageBox.warning(
                self, "Error", "Cannot load preset while Config dialog is open."
            )
            cfg.set_next_to_load("")
            return

        core.reload(reload_preset=True)
        app_signal.refresh.emit(True)

    @Slot()
    def quit_app(self):
        logger.info("Shutting down TinyUi...")
        self._save_window_state()

        try:
            app_signal.hotkey.disconnect()
            app_signal.updates.disconnect()
            app_signal.refresh.disconnect()
            app_signal.quitapp.disconnect()
            app_signal.reload.disconnect()
        except RuntimeError:
            pass

        if self._tray_icon:
            self._tray_icon.hide()

        core.close()
        QApplication.quit()

    def closeEvent(self, event):
        if cfg.application["minimize_to_tray"]:
            event.ignore()
            self.hide()
        else:
            self.quit_app()

    def show_app(self):
        """Show window (for tray double-click and menu)."""
        self.showNormal()
        self.activateWindow()


# --- Entry point ---

def run():
    """Main entry point."""
    _init_config()
    _init_logging()
    app = _init_qt()

    if not _check_single_instance():
        QMessageBox.warning(None, "TinyUi", "TinyUi is already running!")
        return 1

    core.start()
    logger.info(f"TinyPedal: {TP_VERSION}")

    window = MainWindow()
    window.show()

    logger.info("TinyUi ready!")
    return app.exec_()
