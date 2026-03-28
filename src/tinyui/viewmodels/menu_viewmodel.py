#  TinyUI
#  Copyright (C) 2026 Oost-hash
#
#  This file is part of TinyUI.
#
#  TinyUI is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  TinyUI is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#  TinyUI builds on TinyPedal by s-victor (https://github.com/s-victor/TinyPedal),
#  licensed under GPLv3.

from PySide6.QtCore import Property, QObject, QTimer, Signal, Slot
from PySide6.QtQml import QmlElement

from tinycore.logging import get_logger

QML_IMPORT_NAME = "TinyUI"
QML_IMPORT_MAJOR_VERSION = 1

log = get_logger(__name__)


@QmlElement
class MenuViewModel(QObject):
    """Manages the state of the hamburger menu and associated popups.

    QML only calls slots and binds to properties — all logic
    (dismiss, transition, auto-close timer) lives here.
    """

    menuOpenChanged = Signal()
    activePopupChanged = Signal()
    dropdownOpenChanged = Signal()

    _CLOSE_DELAY_MS = 5000

    def __init__(self, parent=None):
        super().__init__(parent)
        self._menu_open: bool = False
        self._active_popup: str = ""  # "" | "help" | "about"
        self._dropdown_open: bool = (
            False  # only True on explicit open, not on popup dismiss
        )
        self._dismissed: str = ""  # name of the popup the user deliberately closed
        self._blocked: str = ""  # briefly blocked after closing (QML overlay-hover guard)

        self._close_timer = QTimer(self)
        self._close_timer.setSingleShot(True)
        self._close_timer.setInterval(self._CLOSE_DELAY_MS)
        self._close_timer.timeout.connect(self._on_close_timer)

    # ── Properties ────────────────────────────────────────────────────────

    @Property(bool, notify=menuOpenChanged)
    def menuOpen(self) -> bool:
        return self._menu_open

    @Property(str, notify=activePopupChanged)
    def activePopup(self) -> str:
        return self._active_popup

    @Property(bool, notify=dropdownOpenChanged)
    def dropdownOpen(self) -> bool:
        return self._dropdown_open

    # ── Slots (called from QML) ───────────────────────────────────────────

    def _snap(self) -> dict:
        return dict(
            open=self._menu_open, active=self._active_popup, dismissed=self._dismissed
        )

    @Slot()
    def toggleMenu(self):
        """Hamburger button or TinyUI label clicked."""
        log.menu("toggleMenu", **self._snap())
        if self._menu_open:
            self._close()
        else:
            self._set_menu_open(True)
            self._set_dropdown_open(True)
        self._close_timer.stop()

    @Slot()
    def closeMenu(self):
        """Close menu and all popups (e.g. after Settings navigation)."""
        log.menu("closeMenu", **self._snap())
        self._close()

    @Slot(str)
    def hoverPopup(self, name: str):
        """Mouse moves over a menu button — open if not dismissed or blocked."""
        blocked = (
            not self._menu_open or self._dismissed == name or self._blocked == name
        )
        log.mouse("hoverPopup", name=name, blocked=blocked, **self._snap())
        if not blocked:
            self._set_active(name)
            self._set_dropdown_open(False)

    @Slot(str)
    def clickPopup(self, name: str):
        """Click on a menu button — toggle; explicit click resets dismiss."""
        log.menu("clickPopup", name=name, **self._snap())
        if self._active_popup == name:
            self._dismissed = name
            self._set_active("")
            self._set_dropdown_open(False)
        else:
            self._dismissed = ""
            self._set_active(name)
            self._set_dropdown_open(False)

    @Slot()
    def closeActivePopup(self):
        """Close current popup without dismiss (hover back to hamburger)."""
        log.menu("closeActivePopup", **self._snap())
        self._set_active("")
        self._set_dropdown_open(True)

    @Slot()
    def dismissActivePopup(self):
        """Click outside menu zone — close popup or dropdown, start timer."""
        log.menu("dismissActivePopup", **self._snap())
        if self._active_popup:
            self._dismissed = self._active_popup
            self._set_active("")
        self._set_dropdown_open(False)
        if self._menu_open:
            self._close_timer.start()

    @Slot()
    def mouseEnteredMenu(self):
        """Mouse is in the menu zone — stop auto-close timer."""
        log.mouse("entered", **self._snap())
        self._close_timer.stop()

    @Slot()
    def mouseLeftMenu(self):
        """Mouse leaves the menu zone — start auto-close timer."""
        log.mouse("left", **self._snap())
        if self._menu_open:
            self._close_timer.start()

    # ── Intern ────────────────────────────────────────────────────────────

    def _set_menu_open(self, val: bool) -> None:
        if self._menu_open != val:
            self._menu_open = val
            self.menuOpenChanged.emit()

    def _set_dropdown_open(self, val: bool) -> None:
        if self._dropdown_open != val:
            self._dropdown_open = val
            self.dropdownOpenChanged.emit()

    def _set_active(self, name: str) -> None:
        if self._active_popup != name:
            prev = self._active_popup
            self._active_popup = name
            log.menu("activePopup", prev=prev, new=name)
            self.activePopupChanged.emit()
            if name:
                self._close_timer.stop()
            if prev:
                self._blocked = prev
                log.menu("blocking", popup=prev, ms=100)
                QTimer.singleShot(100, lambda p=prev: self._unblock(p))

    def _unblock(self, name: str) -> None:
        if self._blocked == name:
            log.menu("unblocked", popup=name)
            self._blocked = ""

    def _close(self) -> None:
        """Close everything and reset all state for the next session."""
        log.menu("close")
        self._dismissed = ""
        self._blocked = ""
        self._set_active("")
        self._set_dropdown_open(False)
        self._set_menu_open(False)
        self._close_timer.stop()

    def _on_close_timer(self) -> None:
        self._close()
