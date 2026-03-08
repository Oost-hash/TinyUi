#
#  TinyUi - Window Menu
#  Copyright (C) 2025 Oost-hash
#

"""Window menu."""

from PySide2.QtWidgets import QMenu

from tinyui.backend.constants import ConfigType
from tinyui.backend.controls import loader
from tinyui.backend.settings import cfg
from .. import _store as store


class WindowMenu(QMenu):
    """Window menu"""

    def __init__(self, title, parent):
        super().__init__(title, parent)
        self.show_at_startup = self.addAction("Show at Startup")
        self.show_at_startup.setCheckable(True)
        self.show_at_startup.triggered.connect(self.is_show_at_startup)

        self.minimize_to_tray = self.addAction("Minimize to Tray")
        self.minimize_to_tray.setCheckable(True)
        self.minimize_to_tray.triggered.connect(self.is_minimize_to_tray)

        self.remember_position = self.addAction("Remember Position")
        self.remember_position.setCheckable(True)
        self.remember_position.triggered.connect(self.is_remember_position)

        self.remember_size = self.addAction("Remember Size")
        self.remember_size.setCheckable(True)
        self.remember_size.triggered.connect(self.is_remember_size)
        self.addSeparator()

        restart_app = self.addAction("Restart TinyPedal")
        restart_app.triggered.connect(loader.restart)

        self.aboutToShow.connect(self.refresh_menu)

    def refresh_menu(self):
        """Refresh menu"""
        self.show_at_startup.setChecked(cfg.application["show_at_startup"])
        self.minimize_to_tray.setChecked(cfg.application["minimize_to_tray"])
        self.remember_position.setChecked(cfg.application["remember_position"])
        self.remember_size.setChecked(cfg.application["remember_size"])

    def is_show_at_startup(self):
        """Toggle config window startup state"""
        store.toggle(cfg.application, "show_at_startup", ConfigType.CONFIG)

    def is_minimize_to_tray(self):
        """Toggle minimize to tray state"""
        store.toggle(cfg.application, "minimize_to_tray", ConfigType.CONFIG)

    def is_remember_position(self):
        """Toggle config window remember position state"""
        store.toggle(cfg.application, "remember_position", ConfigType.CONFIG)

    def is_remember_size(self):
        """Toggle config window remember size state"""
        store.toggle(cfg.application, "remember_size", ConfigType.CONFIG)
