#
#  TinyUi - Main Window
#  Copyright (C) 2026 Oost-hash
#

"""TinyUi main window."""

import logging

from PySide2.QtCore import Qt, Slot
from PySide2.QtWidgets import (
    QApplication,
    QMainWindow,
    QMessageBox,
)

from tinyui.backend.constants import TP_APP_NAME, TP_VERSION, ConfigType
from tinyui.backend.controls import app_signal
from tinyui.backend.core_loader import core
from tinyui.backend.settings import cfg
from tinyui.themes.style import set_style_palette, set_style_window
from tinyui.version import __version__ as TINYUI_VERSION

from ._common import DialogSingleton, UIScaler
from .components.status_bar import StatusButtonBar
from .components.tab_view import TabView
from .menus import APIMenu, ConfigMenu, HelpMenu, OverlayMenu, ToolsMenu, WindowMenu

logger = logging.getLogger("TinyUi")


class MainWindow(QMainWindow):
    """TinyUi main window."""

    def __init__(self):
        super().__init__()
        self._tray = None
        self.setWindowTitle(f"TinyUi v{TINYUI_VERSION} | {TP_APP_NAME} v{TP_VERSION}")
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        self._last_style = None

        self._setup_statusbar()
        self._setup_menubar()
        self._setup_tabs()
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

        if self._tray:
            self._tray.hide()

        core.close()
        QApplication.quit()

    def set_tray(self, tray):
        """Attach the tray icon so quit_app can hide it."""
        self._tray = tray

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
