#
#  TinyUi - Overlay Menu
#  Copyright (C) 2025 Oost-hash
#

"""Overlay menu, shared between main window and tray."""

import os

from PySide2.QtWidgets import QMenu, QMessageBox

from tinyui.backend.controls import api, octrl
from tinyui.backend.misc import minfo
from tinyui.backend.settings import cfg


class OverlayMenu(QMenu):
    """Overlay menu, shared between main & tray menu"""

    def __init__(self, title, parent, is_tray: bool = False):
        super().__init__(title, parent)
        if is_tray:
            self._parent = parent
            loaded_preset_font = self.font()
            loaded_preset_font.setBold(True)
            self.loaded_preset = self.addAction("")
            self.loaded_preset.setFont(loaded_preset_font)
            self.loaded_preset.triggered.connect(self.open_preset_tab)
            self.aboutToShow.connect(self.refresh_preset_name)
            self.addSeparator()

            app_config = self.addAction("Config")
            app_config.triggered.connect(parent.show_app)
            self.addSeparator()

        # Lock overlay
        self.overlay_lock = self.addAction("Lock Overlay")
        self.overlay_lock.setCheckable(True)
        self.overlay_lock.triggered.connect(self.is_locked)

        # Auto hide
        self.overlay_hide = self.addAction("Auto Hide")
        self.overlay_hide.setCheckable(True)
        self.overlay_hide.triggered.connect(self.is_hidden)

        # Grid move
        self.overlay_grid = self.addAction("Grid Move")
        self.overlay_grid.setCheckable(True)
        self.overlay_grid.triggered.connect(self.has_grid)

        # VR Compatbiility
        self.overlay_vr = self.addAction("VR Compatibility")
        self.overlay_vr.setCheckable(True)
        self.overlay_vr.triggered.connect(self.vr_compatibility)

        # Reload preset (check for opened config dialog)
        reload_preset = self.addAction("Reload")
        reload_preset.triggered.connect(parent.reload_preset)
        self.addSeparator()

        # Reset submenu
        menu_reset_data = ResetDataMenu("Reset Data", parent)
        self.addMenu(menu_reset_data)
        self.addSeparator()

        # Quit
        app_quit = self.addAction("Quit")
        app_quit.triggered.connect(parent.quit_app)

        # Refresh menu
        self.aboutToShow.connect(self.refresh_menu)

    def refresh_menu(self):
        """Refresh menu"""
        self.overlay_lock.setChecked(cfg.overlay["fixed_position"])
        self.overlay_hide.setChecked(cfg.overlay["auto_hide"])
        self.overlay_grid.setChecked(cfg.overlay["enable_grid_move"])
        self.overlay_vr.setChecked(cfg.overlay["vr_compatibility"])

    def refresh_preset_name(self):
        """Refresh preset name"""
        loaded_preset = cfg.filename.setting[:-5]
        if len(loaded_preset) > 16:
            loaded_preset = f"{loaded_preset[:16]}..."
        self.loaded_preset.setText(loaded_preset)

    def open_preset_tab(self):
        """Open preset tab"""
        self._parent.centralWidget().select_preset_tab()
        self._parent.show_app()

    @staticmethod
    def is_locked():
        """Check lock state"""
        octrl.toggle.lock()

    @staticmethod
    def is_hidden():
        """Check hide state"""
        octrl.toggle.hide()

    @staticmethod
    def has_grid():
        """Check grid move state"""
        octrl.toggle.grid()

    @staticmethod
    def vr_compatibility():
        """Check VR compatibility state"""
        octrl.toggle.vr()


class ResetDataMenu(QMenu):
    """Reset user data menu"""

    def __init__(self, title, parent):
        super().__init__(title, parent)
        self._parent = parent

        reset_deltabest = self.addAction("Delta Best")
        reset_deltabest.triggered.connect(self.reset_deltabest)

        reset_energydelta = self.addAction("Energy Delta")
        reset_energydelta.triggered.connect(self.reset_energydelta)

        reset_fueldelta = self.addAction("Fuel Delta")
        reset_fueldelta.triggered.connect(self.reset_fueldelta)

        reset_consumption = self.addAction("Consumption History")
        reset_consumption.triggered.connect(self.reset_consumption)

        reset_sectorbest = self.addAction("Sector Best")
        reset_sectorbest.triggered.connect(self.reset_sectorbest)

        reset_trackmap = self.addAction("Track Map")
        reset_trackmap.triggered.connect(self.reset_trackmap)

    def reset_deltabest(self):
        """Reset deltabest data"""
        self.__confirmation(
            data_type="delta best",
            extension="csv",
            filepath=cfg.path.delta_best,
            filename=api.read.session.combo_name(),
        )

    def reset_energydelta(self):
        """Reset energy delta data"""
        self.__confirmation(
            data_type="energy delta",
            extension="energy",
            filepath=cfg.path.energy_delta,
            filename=api.read.session.combo_name(),
        )

    def reset_fueldelta(self):
        """Reset fuel delta data"""
        self.__confirmation(
            data_type="fuel delta",
            extension="fuel",
            filepath=cfg.path.fuel_delta,
            filename=api.read.session.combo_name(),
        )

    def reset_consumption(self):
        """Reset consumption history data"""
        if self.__confirmation(
            data_type="consumption history",
            extension="consumption",
            filepath=cfg.path.fuel_delta,
            filename=api.read.session.combo_name(),
        ):
            minfo.history.reset_consumption()

    def reset_sectorbest(self):
        """Reset sector best data"""
        self.__confirmation(
            data_type="sector best",
            extension="sector",
            filepath=cfg.path.sector_best,
            filename=api.read.session.combo_name(),
        )

    def reset_trackmap(self):
        """Reset trackmap data"""
        self.__confirmation(
            data_type="track map",
            extension="svg",
            filepath=cfg.path.track_map,
            filename=api.read.session.track_name(),
        )

    def __confirmation(self, data_type: str, extension: str, filepath: str, filename: str) -> bool:
        """Message confirmation, returns true if file deleted"""
        # Check if on track
        if api.read.state.active():
            QMessageBox.warning(
                self._parent,
                "Error",
                "Cannot reset data while on track.",
            )
            return False
        # Check if file exist
        filename_full = f"{filepath}{filename}.{extension}"
        if not os.path.exists(filename_full):
            QMessageBox.warning(
                self._parent,
                "Error",
                f"No {data_type} data found.<br><br>You can only reset data from active session.",
            )
            return False
        # Confirm reset
        msg_text = (
            f"Reset <b>{data_type}</b> data for<br>"
            f"<b>{filename}</b> ?<br><br>"
            "This cannot be undone!"
        )
        delete_msg = QMessageBox.question(
            self._parent, f"Reset {data_type.title()}", msg_text,
            buttons=QMessageBox.Yes | QMessageBox.No,
            defaultButton=QMessageBox.No,
        )
        if delete_msg != QMessageBox.Yes:
            return False
        # Delete file
        os.remove(filename_full)
        QMessageBox.information(
            self._parent,
            f"Reset {data_type.title()}",
            f"{data_type.capitalize()} data has been reset for<br><b>{filename}</b>",
        )
        return True
