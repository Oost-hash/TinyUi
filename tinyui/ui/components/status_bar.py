#
#  TinyUi - Status Bar
#  Copyright (C) 2026 Oost-hash
#

"""Status button bar component."""

from PySide2.QtCore import Slot
from PySide2.QtWidgets import QMessageBox, QPushButton, QStatusBar

from tinyui.backend.constants import ConfigType
from tinyui.backend.controls import api, app_signal, loader
from tinyui.backend.settings import cfg


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
            self,
            "High DPI Scaling",
            msg_text,
            buttons=QMessageBox.Yes | QMessageBox.No,
            defaultButton=QMessageBox.No,
        )
        if restart_msg != QMessageBox.Yes:
            return

        cfg.application["enable_high_dpi_scaling"] = not cfg.application[
            "enable_high_dpi_scaling"
        ]
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
