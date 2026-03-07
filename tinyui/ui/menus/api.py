#
#  TinyUi - API Menu
#  Copyright (C) 2025 Oost-hash
#

"""API menu."""

import os

from PySide2.QtWidgets import QMenu, QMessageBox

from tinyui.backend.controls import api, loader
from tinyui.backend.constants import ConfigType
from tinyui.backend.settings import cfg
from ..editors.config import UserConfig
from ._commands import menu_reload_only, menu_refresh_only, menu_restart_api


class APIMenu(QMenu):
    """API menu"""

    def __init__(self, title, parent):
        super().__init__(title, parent)
        self._parent = parent

        # API selector
        self.actions_api = self.__api_selector()
        self.addSeparator()

        self.api_selection = self.addAction("Remember API Selection from Preset")
        self.api_selection.setCheckable(True)
        self.api_selection.triggered.connect(self.toggle_api_selection)

        self.legacy_api = self.addAction("Enable Legacy API Selection")
        self.legacy_api.setCheckable(True)
        self.legacy_api.triggered.connect(self.toggle_legacy_api)

        self.carsetup_backup = self.addAction("Enable Auto Backup Car Setup")
        self.carsetup_backup.setCheckable(True)
        self.carsetup_backup.triggered.connect(self.toggle_carsetup_backup)

        config_api = self.addAction("Options")
        config_api.triggered.connect(self.open_config_api)
        self.addSeparator()

        restart_api = self.addAction("Restart API")
        restart_api.triggered.connect(menu_restart_api)

        self.aboutToShow.connect(self.refresh_menu)

    def refresh_menu(self):
        """Refresh menu"""
        selected_api_name = cfg.api_name
        for action in self.actions_api.actions():
            if selected_api_name == action.text():
                action.setChecked(True)
                break
        self.api_selection.setChecked(cfg.telemetry["enable_api_selection_from_preset"])
        self.carsetup_backup.setChecked(cfg.telemetry["enable_auto_backup_car_setup"])
        self.legacy_api.setChecked(cfg.telemetry["enable_legacy_api_selection"])

    def toggle_api_selection(self):
        """Toggle API selection mode"""
        enabled = cfg.telemetry["enable_api_selection_from_preset"]
        cfg.telemetry["enable_api_selection_from_preset"] = not enabled
        cfg.save(cfg_type=ConfigType.CONFIG)
        menu_reload_only()

    def toggle_carsetup_backup(self):
        """Toggle auto car setup backup"""
        enabled = cfg.telemetry["enable_auto_backup_car_setup"]
        cfg.telemetry["enable_auto_backup_car_setup"] = not enabled
        cfg.save(cfg_type=ConfigType.CONFIG)
        menu_refresh_only()

    def toggle_legacy_api(self):
        """Toggle legacy API selection"""
        enabled = cfg.telemetry["enable_legacy_api_selection"]
        if enabled:
            state = "Disable"
        else:
            state = "Enable"
        msg_text = (
            f"{state} <b>Legacy API</b> selection and restart <b>TinyPedal</b>?"
        )
        restart_msg = QMessageBox.question(
            self._parent, "Legacy API", msg_text,
            buttons=QMessageBox.Yes | QMessageBox.No,
            defaultButton=QMessageBox.No,
        )
        if restart_msg != QMessageBox.Yes:
            return
        cfg.telemetry["enable_legacy_api_selection"] = not enabled
        cfg.save(cfg_type=ConfigType.CONFIG)
        loader.restart()

    def open_config_api(self):
        """Config API"""
        _dialog = UserConfig(
            parent=self._parent,
            key_name=cfg.api_key,
            cfg_type=ConfigType.SETTING,
            user_setting=cfg.user.setting,
            default_setting=cfg.default.setting,
            reload_func=menu_restart_api,
        )
        _dialog.open()

    def __api_selector(self):
        """Generate API selector"""
        if os.getenv("PYSIDE_OVERRIDE") == "6":
            from PySide6.QtGui import QActionGroup
        else:
            from PySide2.QtWidgets import QActionGroup

        actions_api = QActionGroup(self)

        for _api in api.available:
            api_name = _api.NAME
            option = self.addAction(api_name)
            option.setCheckable(True)
            option.triggered.connect(lambda checked=True, name=api_name: self.__toggle_option(checked, name))
            actions_api.addAction(option)
        return actions_api

    def __toggle_option(self, checked: bool, api_name: str):
        """Toggle option"""
        if cfg.api_name == api_name:
            return
        cfg.api_name = api_name
        if cfg.telemetry["enable_api_selection_from_preset"]:
            save_type = ConfigType.SETTING
        else:
            save_type = ConfigType.CONFIG
        cfg.save(cfg_type=save_type)
        menu_reload_only()
