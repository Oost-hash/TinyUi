#
#  TinyUi - Tray Icon
#  Copyright (C) 2025 Oost-hash
#

"""System tray icon component."""

from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QMainWindow, QSystemTrayIcon

from .menus import OverlayMenu


class TrayIcon(QSystemTrayIcon):
    """Self-contained system tray icon."""

    def __init__(self, icon: QIcon, window: QMainWindow):
        super().__init__(icon, parent=window)
        self.setToolTip(window.windowTitle())
        self.setContextMenu(OverlayMenu("Overlay", window, True))
        self.activated.connect(
            lambda reason: window.show_app()
            if reason == QSystemTrayIcon.ActivationReason.DoubleClick
            else None
        )
