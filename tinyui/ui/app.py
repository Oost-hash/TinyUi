#  TinyPedal is an open-source overlay application for racing simulation.
#  Copyright (C) 2022-2026 TinyPedal developers, see contributors.md file
#
#  This file is part of TinyPedal.
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
Main application window
"""

import logging
from typing import Callable

from PySide2.QtCore import Qt, Slot
from PySide2.QtWidgets import (
    QApplication,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStatusBar,
    QSystemTrayIcon,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from tinypedal import app_signal, loader
from tinypedal.api_control import api
from tinypedal.const_app import APP_NAME, VERSION
from tinypedal.const_file import ConfigType
from tinypedal.module_control import mctrl, wctrl
from tinypedal.setting import cfg
from . import set_style_palette, set_style_window
from ._common import DialogSingleton, UIScaler
from .menu import APIMenu, ConfigMenu, HelpMenu, OverlayMenu, ToolsMenu, WindowMenu
from .notification import NotifyBar
from .views.hotkey_view import HotkeyList
from .views.module_view import ModuleList
from .views.pace_notes_view import PaceNotesControl
from .views.preset_view import PresetList
from .views.spectate_view import SpectateList

logger = logging.getLogger(__name__)

# Tab definitions: (label, factory)
# factory is a callable(parent) -> QWidget
TAB_DEFS = [
    ("Widget",   lambda parent: ModuleList(parent, wctrl)),
    ("Module",   lambda parent: ModuleList(parent, mctrl)),
    ("Preset",   lambda parent: PresetList(parent)),
    ("Spectate", lambda parent: SpectateList(parent)),
    ("Pacenotes", lambda parent: PaceNotesControl(parent)),
    ("Hotkey",   lambda parent: HotkeyList(parent)),
]

# Menu definitions: (label, class)
MENU_DEFS = [
    ("Overlay", OverlayMenu),
    ("API",     APIMenu),
    ("Config",  ConfigMenu),
    ("Tools",   ToolsMenu),
    ("Window",  WindowMenu),
    ("Help",    HelpMenu),
]


class TabView(QWidget):
    """Tab view"""

    def __init__(self, parent):
        super().__init__(parent)
        # Notify bar
        notify_bar = NotifyBar(self)

        # Build tabs from definitions
        self._tabs = QTabWidget(self)
        self._tab_index = {}
        for label, factory in TAB_DEFS:
            tab = factory(self)
            self._tabs.addTab(tab, label)
            self._tab_index[label] = self._tabs.count() - 1
            app_signal.refresh.connect(tab.refresh)
        self._tabs.currentChanged.connect(self.refresh)

        # Connect notify bar buttons to tabs
        notify_bar.presetlocked.clicked.connect(lambda: self.select_tab("Preset"))
        notify_bar.spectate.clicked.connect(lambda: self.select_tab("Spectate"))
        notify_bar.pacenotes.clicked.connect(lambda: self.select_tab("Pacenotes"))
        notify_bar.hotkey.clicked.connect(lambda: self.select_tab("Hotkey"))

        # Main view
        layout_main = QVBoxLayout()
        layout_main.setContentsMargins(0, 0, 0, 0)
        layout_main.setSpacing(0)
        layout_main.addWidget(self._tabs)
        layout_main.addWidget(notify_bar)
        self.setLayout(layout_main)

        # Connect app signal
        app_signal.updates.connect(notify_bar.updates.checking)
        app_signal.refresh.connect(notify_bar.refresh)

    def refresh(self):
        """Refresh tab area"""
        # Workaround to correct tab scroll area size after height changed
        width = self.width()
        height = self.height()
        self.resize(width, height - 1)
        self.resize(width, height + 1)

    def select_tab(self, label: str):
        """Select tab by label"""
        self._tabs.setCurrentIndex(self._tab_index[label])

    def select_preset_tab(self):
        """Select preset tab"""
        self.select_tab("Preset")


class StatusButtonBar(QStatusBar):
    """Status button bar"""

    def __init__(self, parent):
        super().__init__(parent)
        self.button_api = QPushButton("")
        self.button_api.clicked.connect(self.refresh)
        self.button_api.setToolTip("Config Telemetry API")

        self.button_style = QPushButton("")
        self.button_style.clicked.connect(self.toggle_color_theme)
        self.button_style.setToolTip("Toggle Window Color Theme")

        self.button_dpiscale = QPushButton("")
        self.button_dpiscale.clicked.connect(self.toggle_dpi_scaling)
        self.button_dpiscale.setToolTip("Toggle High DPI Scaling")
        self._last_dpi_scaling = cfg.application["enable_high_dpi_scaling"]

        self.addPermanentWidget(self.button_api)
        self.addWidget(self.button_style)
        self.addWidget(self.button_dpiscale)

        app_signal.refresh.connect(self.refresh)

    @Slot(bool)  # type: ignore[operator]
    def refresh(self):
        """Refresh status bar"""
        if cfg.api["enable_active_state_override"]:
            text_api_status = "overriding"
        else:
            text_api_status = api.read.state.version()
        self.button_api.setText(f"API: {api.alias} ({text_api_status})")

        self.button_style.setText(f"UI: {cfg.application['window_color_theme']}")

        if cfg.application["enable_high_dpi_scaling"]:
            text_dpi = "Auto"
        else:
            text_dpi = "Off"
        if self._last_dpi_scaling != cfg.application["enable_high_dpi_scaling"]:
            text_need_restart = "*"
        else:
            text_need_restart = ""
        self.button_dpiscale.setText(f"Scale: {text_dpi}{text_need_restart}")

    def toggle_dpi_scaling(self):
        """Toggle DPI scaling"""
        if cfg.application["enable_high_dpi_scaling"]:
            state = "Disable"
            desc = "not be scaled under high DPI screen resolution."
        else:
            state = "Enable"
            desc = "be auto-scaled according to system DPI scaling setting."
        msg_text = (
            f"{state} <b>High DPI Scaling</b> and restart <b>TinyPedal</b>?<br><br>"
            f"<b>Window</b> and <b>Overlay</b> size and position will {desc}"
        )
        restart_msg = QMessageBox.question(
            self, "High DPI Scaling", msg_text,
            buttons=QMessageBox.Yes | QMessageBox.No,
            defaultButton=QMessageBox.No,
        )
        if restart_msg != QMessageBox.Yes:
            return

        cfg.application["enable_high_dpi_scaling"] = not cfg.application["enable_high_dpi_scaling"]
        cfg.save(cfg_type=ConfigType.CONFIG)
        loader.restart()

    def toggle_color_theme(self):
        """Toggle color theme"""
        if cfg.application["window_color_theme"] == "Dark":
            cfg.application["window_color_theme"] = "Light"
        else:
            cfg.application["window_color_theme"] = "Dark"
        cfg.save(cfg_type=ConfigType.CONFIG)
        app_signal.refresh.emit(True)


class AppWindow(QMainWindow):
    """Main application window"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} v{VERSION}")
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        self.last_style = None

        # Status bar
        self.setStatusBar(StatusButtonBar(self))

        # Menu bar
        self.set_menu_bar()

        # Tab view
        self.setCentralWidget(TabView(self))

        # Tray icon
        self.set_tray_icon()

        # Window state
        self.set_window_state()
        self.__connect_signal()

        # Refresh GUI
        app_signal.refresh.emit(True)

    @Slot(bool)  # type: ignore[operator]
    def refresh(self):
        """Refresh GUI"""
        # Window style
        style = cfg.application["window_color_theme"]
        if self.last_style != style:
            self.last_style = style
            set_style_palette(self.last_style)
            self.setStyleSheet(set_style_window(QApplication.font().pointSize()))
            logger.info("GUI: loading window color theme: %s", style)

    def set_menu_bar(self):
        """Set menu bar"""
        logger.info("GUI: loading window menu")
        menu = self.menuBar()
        menus = {}
        for label, menu_class in MENU_DEFS:
            m = menu_class(label, self)
            menu.addMenu(m)
            menus[label] = m
        # Link API menu to status bar button
        self.statusBar().button_api.setMenu(menus["API"])

    def set_tray_icon(self):
        """Set tray icon"""
        logger.info("GUI: loading tray icon")
        tray_icon = QSystemTrayIcon(self)
        # Config tray icon
        tray_icon.setIcon(self.windowIcon())
        tray_icon.setToolTip(self.windowTitle())
        tray_icon.activated.connect(self.tray_doubleclick)
        # Add tray menu
        tray_menu = OverlayMenu("Overlay", self, True)
        tray_icon.setContextMenu(tray_menu)
        tray_icon.show()

    def tray_doubleclick(self, active_reason: QSystemTrayIcon.ActivationReason):
        """Tray doubleclick"""
        if active_reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_app()

    def set_window_state(self):
        """Set initial window state"""
        self.setMinimumSize(UIScaler.size(23), UIScaler.size(36))
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, False)  # disable maximize

        if cfg.application["remember_size"]:
            self.resize(
                cfg.application["window_width"],
                cfg.application["window_height"],
            )

        if cfg.application["remember_position"]:
            self.load_window_position()

        if cfg.compatibility["enable_window_position_correction"]:
            self.verify_window_position()

        if cfg.application["show_at_startup"]:
            self.showNormal()
        elif not cfg.application["minimize_to_tray"]:
            self.showMinimized()

    def load_window_position(self):
        """Load window position"""
        logger.info("GUI: loading window setting")
        app_pos_x = cfg.application["position_x"]
        app_pos_y = cfg.application["position_y"]
        # Save new x,y position if preset value at 0,0
        if 0 == app_pos_x == app_pos_y:
            self.save_window_state()
        else:
            self.move(app_pos_x, app_pos_y)

    def verify_window_position(self):
        """Verify window position"""
        # Get screen size from the screen where app window located
        screen_geo = self.screen().geometry()
        # Limiting position value if out of screen range
        app_pos_x = min(
            max(self.x(), screen_geo.left()),
            screen_geo.right() - self.minimumWidth(),
        )
        app_pos_y = min(
            max(self.y(), screen_geo.top()),
            screen_geo.bottom() - self.minimumHeight(),
        )
        # Re-adjust position only if mismatched
        if self.x() != app_pos_x or self.y() != app_pos_y:
            self.move(app_pos_x, app_pos_y)
            logger.info("GUI: window position corrected")

    def save_window_state(self):
        """Save window state"""
        save_changes = False

        if cfg.application["remember_position"]:
            last_pos = cfg.application["position_x"], cfg.application["position_y"]
            new_pos = self.x(), self.y()
            if last_pos != new_pos:
                cfg.application["position_x"] = new_pos[0]
                cfg.application["position_y"] = new_pos[1]
                save_changes = True

        if cfg.application["remember_size"]:
            last_size = cfg.application["window_width"], cfg.application["window_height"]
            new_size = self.width(), self.height()
            if last_size != new_size:
                cfg.application["window_width"] = new_size[0]
                cfg.application["window_height"] = new_size[1]
                save_changes = True

        if save_changes:
            cfg.save(0, cfg_type=ConfigType.CONFIG)

    def show_app(self):
        """Show app window"""
        self.showNormal()
        self.activateWindow()

    @Slot(bool)  # type: ignore[operator]
    def quit_app(self):
        """Quit manager"""
        loader.close()  # must close this first
        self.save_window_state()
        self.__break_signal()
        self.findChild(QSystemTrayIcon).hide()  # workaround tray icon not removed after exited
        QApplication.quit()

    def closeEvent(self, event):
        """Minimize to tray"""
        if cfg.application["minimize_to_tray"]:
            event.ignore()
            self.hide()
        else:
            self.quit_app()

    @Slot(bool)  # type: ignore[operator]
    def reload_preset(self, check_singleton: bool):
        """Reload current preset"""
        # Cancel loading while any config dialog opened
        if check_singleton and DialogSingleton.is_opened(ConfigType.CONFIG):
            msg_text = "Cannot load preset while Config dialog is opened."
            QMessageBox.warning(self, "Error", msg_text)
            cfg.set_next_to_load("")
            return
        loader.reload(reload_preset=True)
        app_signal.refresh.emit(True)

    @Slot(object)  # type: ignore[operator]
    def hotkey_command(self, hotkey_func: Callable):
        """Hotkey command must be run in main thread"""
        hotkey_func()

    def __connect_signal(self):
        """Connect signal"""
        app_signal.hotkey.connect(self.hotkey_command)
        app_signal.refresh.connect(self.refresh)
        app_signal.quitapp.connect(self.quit_app)
        app_signal.reload.connect(self.reload_preset)
        logger.info("GUI: connect signals")

    def __break_signal(self):
        """Disconnect signal"""
        app_signal.hotkey.disconnect()
        app_signal.updates.disconnect()
        app_signal.refresh.disconnect()
        app_signal.quitapp.disconnect()
        app_signal.reload.disconnect()
        logger.info("GUI: disconnect signals")
