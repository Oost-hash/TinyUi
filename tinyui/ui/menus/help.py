#
#  TinyUi - Help Menu
#  Copyright (C) 2025 Oost-hash
#

"""Help menu."""

from PySide2.QtGui import QDesktopServices
from PySide2.QtWidgets import QMenu

from tinyui.backend.constants import URL_FAQ, URL_USER_GUIDE
from tinyui.backend.misc import update_checker
from ..dialogs.about import About
from ..dialogs.log_info import LogInfo


class HelpMenu(QMenu):
    """Help menu"""

    def __init__(self, title, parent):
        super().__init__(title, parent)
        self._parent = parent

        app_guide = self.addAction("User Guide")
        app_guide.triggered.connect(self.open_user_guide)

        app_faq = self.addAction("Frequently Asked Questions")
        app_faq.triggered.connect(self.open_faq)

        app_log = self.addAction("Show Log")
        app_log.triggered.connect(self.show_log)
        self.addSeparator()

        app_update = self.addAction("Check for Updates")
        app_update.triggered.connect(self.show_update)
        self.addSeparator()

        app_about = self.addAction("About")
        app_about.triggered.connect(self.show_about)

    def show_about(self):
        """Show about"""
        _dialog = About(self._parent)
        _dialog.show()

    def show_log(self):
        """Show log"""
        _dialog = LogInfo(self._parent)
        _dialog.show()

    def show_update(self):
        """Show update"""
        update_checker.check(True)

    def open_user_guide(self):
        """Open user guide link"""
        QDesktopServices.openUrl(URL_USER_GUIDE)

    def open_faq(self):
        """Open FAQ link"""
        QDesktopServices.openUrl(URL_FAQ)
