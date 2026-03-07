#
#  TinyUi - Config Menu
#  Copyright (C) 2025 Oost-hash
#

"""Config menu."""

import os

from PySide2.QtWidgets import QMenu, QMessageBox

from tinyui.backend.constants import PLATFORM, ConfigType
from tinyui.backend.formatter import format_option_name
from tinyui.backend.settings import cfg
from ..dialogs import FontConfig, UserConfig
from ._commands import menu_reload_preset, menu_reload_only, menu_refresh_only


class ConfigMenu(QMenu):
    """Config menu"""

    def __init__(self, title, parent):
        super().__init__(title, parent)
        self._parent = parent

        config_app = self.addAction("Application")
        config_app.triggered.connect(self.open_config_application)

        config_compat = self.addAction("Compatibility")
        config_compat.triggered.connect(self.open_config_compatibility)

        config_notify = self.addAction("Notification")
        config_notify.triggered.connect(self.open_config_notification)
        self.addSeparator()

        config_units = self.addAction("Units")
        config_units.triggered.connect(self.open_config_units)

        config_font = self.addAction("Global Font Override")
        config_font.triggered.connect(self.open_config_font)
        self.addSeparator()

        config_userpath = self.addAction("User Path")
        config_userpath.triggered.connect(self.open_config_userpath)

        open_folder = self.addMenu("Open Folder")
        for path_name in cfg.path.__slots__:
            _folder = open_folder.addAction(format_option_name(path_name))
            _folder.triggered.connect(lambda checked=True, p=path_name: self.open_folder(checked, p))

    def open_folder(self, checked: bool, path_name: str):
        """Open folder in file manager"""
        filepath = getattr(cfg.path, path_name)
        error = False
        if PLATFORM.WINDOWS:
            try:
                filepath = filepath.replace("/", "\\")
                os.startfile(filepath)
            except (FileNotFoundError, RuntimeError):
                error = True
        else:  # Linux
            try:
                import subprocess
                subprocess.run(["xdg-open", filepath])
            except (FileNotFoundError, subprocess.SubprocessError):
                error = True
        if error:
            QMessageBox.warning(
                self._parent,
                "Error",
                f"Cannot open folder:<br><b>{filepath}</b>",
            )

    def open_config_application(self):
        """Config global application"""
        _dialog = UserConfig(
            parent=self._parent,
            key_name="application",
            cfg_type=ConfigType.CONFIG,
            user_setting=cfg.user.config,
            default_setting=cfg.default.config,
            reload_func=menu_reload_preset,
        )
        _dialog.open()

    def open_config_compatibility(self):
        """Config global compatibility"""
        _dialog = UserConfig(
            parent=self._parent,
            key_name="compatibility",
            cfg_type=ConfigType.CONFIG,
            user_setting=cfg.user.config,
            default_setting=cfg.default.config,
            reload_func=menu_reload_preset,
        )
        _dialog.open()

    def open_config_userpath(self):
        """Config global user path"""
        _dialog = UserConfig(
            parent=self._parent,
            key_name="user_path",
            cfg_type=ConfigType.CONFIG,
            user_setting=cfg.user.config,
            default_setting=cfg.default.config,
            reload_func=menu_reload_preset,
            option_width=22,
        )
        _dialog.open()

    def open_config_notification(self):
        """Config GUI notification"""
        _dialog = UserConfig(
            parent=self._parent,
            key_name="notification",
            cfg_type=ConfigType.CONFIG,
            user_setting=cfg.user.config,
            default_setting=cfg.default.config,
            reload_func=menu_refresh_only,
        )
        _dialog.open()

    def open_config_units(self):
        """Config display units"""
        _dialog = UserConfig(
            parent=self._parent,
            key_name="units",
            cfg_type=ConfigType.SETTING,
            user_setting=cfg.user.setting,
            default_setting=cfg.default.setting,
            reload_func=menu_reload_only,
        )
        _dialog.open()

    def open_config_font(self):
        """Config global font"""
        _dialog = FontConfig(
            parent=self._parent,
            user_setting=cfg.user.setting,
            reload_func=menu_reload_only,
        )
        _dialog.open()
