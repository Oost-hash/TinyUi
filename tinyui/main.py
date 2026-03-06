#
#  TinyUi - Main Window
#  Copyright (C) 2025 Oost-hash
#

"""Hoofdvenster - gebruikt gekopieerde TinyPedal UI"""

import logging
import os
import sys

from PySide2.QtCore import Qt, Slot
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import (
    QApplication,
    QMainWindow,
    QMessageBox,
    QSystemTrayIcon,
)

# Alleen imports die geen cfg nodig hebben
from tinyui.version import __version__ as TINYUI_VERSION
from tinyui.backend.constants import TP_APP_NAME, TP_VERSION, ConfigType, ImageFile

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
    # Fallback to TinyPedal icon
    tp_path = os.path.join(_app_root(), ImageFile.APP_ICON)
    if os.path.exists(tp_path):
        return QIcon(tp_path)
    return QIcon()


def _app_root():
    """Geeft het root pad van de applicatie (werkt in frozen en dev mode)"""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tinypedal"
    )


class MainWindow(QMainWindow):
    """TinyUi Hoofdvenster"""

    def __init__(self):
        # LAZY IMPORTS - pas hier, NA dat QApplication en cfg bestaan
        from tinyui.backend.controls import api, app_signal
        from tinyui.backend.settings import cfg

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

        from .core_loader import core

        super().__init__()

        # Bewaar references voor methods
        self._app_signal = app_signal
        self._api = api
        self._cfg = cfg
        self._set_style_palette = set_style_palette
        self._set_style_window = set_style_window
        self._DialogSingleton = DialogSingleton
        self._UIScaler = UIScaler
        self._TabView = TabView
        self._StatusButtonBar = StatusButtonBar
        self._APIMenu = APIMenu
        self._ConfigMenu = ConfigMenu
        self._HelpMenu = HelpMenu
        self._OverlayMenu = OverlayMenu
        self._ToolsMenu = ToolsMenu
        self._WindowMenu = WindowMenu
        self._core = core

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

        self._app_signal.refresh.emit(True)

    def _setup_statusbar(self):
        self.setStatusBar(self._StatusButtonBar(self))

    def _setup_menubar(self):
        logger.info("Loading menu bar...")
        menu = self.menuBar()
        menu.addMenu(self._OverlayMenu("Overlay", self))

        menu_api = self._APIMenu("API", self)
        menu.addMenu(menu_api)
        self.statusBar().button_api.setMenu(menu_api)

        menu.addMenu(self._ConfigMenu("Config", self))
        menu.addMenu(self._ToolsMenu("Tools", self))
        menu.addMenu(self._WindowMenu("Window", self))
        menu.addMenu(self._HelpMenu("Help", self))

    def _setup_tabs(self):
        self.tab_view = self._TabView(self)
        self.setCentralWidget(self.tab_view)

    def _setup_tray(self):
        logger.info("Loading tray icon...")
        tray_icon = QSystemTrayIcon(self)
        tray_icon.setIcon(_load_icon())
        tray_icon.setToolTip(self.windowTitle())
        tray_icon.activated.connect(self._tray_activated)

        tray_menu = self._OverlayMenu("Overlay", self, True)
        tray_icon.setContextMenu(tray_menu)
        tray_icon.show()
        self._tray_icon = tray_icon

    def _tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.showNormal()
            self.activateWindow()

    def _setup_window_state(self):
        self.setMinimumSize(self._UIScaler.size(23), self._UIScaler.size(36))
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, False)

        if self._cfg.application["remember_size"]:
            self.resize(
                self._cfg.application["window_width"],
                self._cfg.application["window_height"],
            )

        if self._cfg.application["remember_position"]:
            self._load_window_position()

        if self._cfg.compatibility["enable_window_position_correction"]:
            self._verify_window_position()

        if self._cfg.application["show_at_startup"]:
            self.showNormal()
        elif not self._cfg.application["minimize_to_tray"]:
            self.showMinimized()

    def _load_window_position(self):
        app_pos_x = self._cfg.application["position_x"]
        app_pos_y = self._cfg.application["position_y"]
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

        if self._cfg.application["remember_position"]:
            last_pos = (
                self._cfg.application["position_x"],
                self._cfg.application["position_y"],
            )
            new_pos = self.x(), self.y()
            if last_pos != new_pos:
                self._cfg.application["position_x"] = new_pos[0]
                self._cfg.application["position_y"] = new_pos[1]
                save_changes = True

        if self._cfg.application["remember_size"]:
            last_size = (
                self._cfg.application["window_width"],
                self._cfg.application["window_height"],
            )
            new_size = self.width(), self.height()
            if last_size != new_size:
                self._cfg.application["window_width"] = new_size[0]
                self._cfg.application["window_height"] = new_size[1]
                save_changes = True

        if save_changes:
            self._cfg.save(0, cfg_type=ConfigType.CONFIG)

    def _connect_signals(self):
        self._app_signal.refresh.connect(self._on_refresh)
        self._app_signal.quitapp.connect(self.quit_app)
        self._app_signal.reload.connect(self.reload_preset)

    @Slot(bool)
    def _on_refresh(self):
        style = self._cfg.application["window_color_theme"]
        if self._last_style != style:
            self._last_style = style
            self._set_style_palette(style)
            self.setStyleSheet(self._set_style_window(QApplication.font().pointSize()))
            logger.info(f"Theme loaded: {style}")

    @Slot(bool)
    def reload_preset(self, check_singleton: bool = True):
        if check_singleton and self._DialogSingleton.is_opened(ConfigType.CONFIG):
            QMessageBox.warning(
                self, "Error", "Cannot load preset while Config dialog is open."
            )
            self._cfg.set_next_to_load("")
            return

        self._core.reload(reload_preset=True)
        self._app_signal.refresh.emit(True)

    @Slot()
    def quit_app(self):
        logger.info("Shutting down TinyUi...")
        self._save_window_state()

        try:
            self._app_signal.hotkey.disconnect()
            self._app_signal.updates.disconnect()
            self._app_signal.refresh.disconnect()
            self._app_signal.quitapp.disconnect()
            self._app_signal.reload.disconnect()
        except RuntimeError:
            pass

        if self._tray_icon:
            self._tray_icon.hide()

        self._core.close()
        QApplication.quit()

    def closeEvent(self, event):
        if self._cfg.application["minimize_to_tray"]:
            event.ignore()
            self.hide()
        else:
            self.quit_app()

    def show_app(self):
        """Toon venster (voor tray double-click en menu)"""
        self.showNormal()
        self.activateWindow()


def run():
    """Main entry point"""
    import io

    from PySide2.QtCore import QCoreApplication, QLocale
    from PySide2.QtGui import QFont, QGuiApplication, QPixmapCache
    from tinypedal.log_handler import set_logging_level
    from tinypedal.main import set_environment, unset_environment
    from tinyui.backend.settings import cfg as _cfg_local

    # 1. Setup environment
    unset_environment()

    # 2. Load config FIRST
    _cfg_local.load_global()
    _cfg_local.save(cfg_type=ConfigType.CONFIG)
    _cfg_local.save(cfg_type=ConfigType.SHORTCUTS)

    # 3. Setup logging
    log_stream = io.StringIO()
    set_logging_level(logger, _cfg_local.path.config, "tinyui.log", log_stream, 2)
    logger.info("=" * 50)
    logger.info("TinyUi v0.2.0 Starting...")

    set_environment()

    # 4. Init GUI
    loc = QLocale(QLocale.C)
    loc.setNumberOptions(QLocale.RejectGroupSeparator)
    QLocale.setDefault(loc)

    if _cfg_local.application["enable_high_dpi_scaling"]:
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

    # 5. Single instance check
    from .core_loader import is_pid_exist, save_pid_file

    if os.getenv("TINYUI_RESTART") == "TRUE":
        os.environ.pop("TINYUI_RESTART", None)
        save_pid_file()
    elif not is_pid_exist():
        save_pid_file()
    else:
        QMessageBox.warning(None, "TinyUi", "TinyUi is already running!")
        return 1

    # 6. Start core
    from .core_loader import core

    core.start()
    logger.info(f"TinyPedal: {TP_VERSION}")

    # 7. Start window
    window = MainWindow()
    window.show()

    logger.info("TinyUi ready!")
    return app.exec_()
