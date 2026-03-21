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

from PySide6.QtCore import QObject, Property, Signal, Slot, QTimer

from qml_poc.log import get_logger

log = get_logger(__name__)


class MenuViewModel(QObject):
    """Beheert de staat van het hamburgermenu en bijbehorende popups.

    QML roept alleen slots aan en bindt aan properties — alle logica
    (dismiss, overstap, auto-close timer) leeft hier.
    """

    menuOpenChanged = Signal()
    activePopupChanged = Signal()
    dropdownOpenChanged = Signal()

    _CLOSE_DELAY_MS = 5000

    def __init__(self, parent=None):
        super().__init__(parent)
        self._menu_open: bool = False
        self._active_popup: str = ""   # "" | "help" | "about"
        self._dropdown_open: bool = False  # alleen True bij expliciete open, niet bij popup-dismiss
        self._dismissed: str = ""      # naam van de popup die de gebruiker bewust sloot
        self._blocked: str = ""        # kort geblokkeerd na sluiten (QML overlay-hover guard)

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

    # ── Slots (aangeroepen vanuit QML) ────────────────────────────────────

    def _snap(self) -> dict:
        return dict(open=self._menu_open, active=self._active_popup,
                    dismissed=self._dismissed)

    @Slot()
    def toggleMenu(self):
        """Hamburger-knop of TinyUi-tekst geklikt."""
        log.menu("toggleMenu", **self._snap())
        if self._menu_open:
            self._close()
        else:
            self._set_menu_open(True)
            self._set_dropdown_open(True)
        self._close_timer.stop()

    @Slot()
    def closeMenu(self):
        """Sluit menu en alle popups (bijv. na Settings navigatie)."""
        log.menu("closeMenu", **self._snap())
        self._close()

    @Slot(str)
    def hoverPopup(self, name: str):
        """Muis beweegt over een menu-knop — open als niet dismissed of geblokkeerd."""
        blocked = not self._menu_open or self._dismissed == name or self._blocked == name
        log.mouse("hoverPopup", name=name, blocked=blocked, **self._snap())
        if not blocked:
            self._set_active(name)
            self._set_dropdown_open(False)

    @Slot(str)
    def clickPopup(self, name: str):
        """Klik op een menu-knop — toggle; expliciete klik reset dismiss."""
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
        """Sluit huidige popup zonder dismiss (hover terug naar hamburger)."""
        log.menu("closeActivePopup", **self._snap())
        self._set_active("")
        self._set_dropdown_open(True)

    @Slot()
    def dismissActivePopup(self):
        """Klik buiten menu-zone — sluit popup of dropdown, start timer."""
        log.menu("dismissActivePopup", **self._snap())
        if self._active_popup:
            self._dismissed = self._active_popup
            self._set_active("")
        self._set_dropdown_open(False)
        if self._menu_open:
            self._close_timer.start()

    @Slot()
    def mouseEnteredMenu(self):
        """Muis is in de menu-zone — stop auto-close timer."""
        log.mouse("entered", **self._snap())
        self._close_timer.stop()

    @Slot()
    def mouseLeftMenu(self):
        """Muis verlaat de menu-zone — start auto-close timer."""
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
            log.state("activePopup", prev=prev, new=name)
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
        """Sluit alles en reset alle state voor de volgende sessie."""
        log.menu("close")
        self._dismissed = ""
        self._blocked = ""
        self._set_active("")
        self._set_dropdown_open(False)
        self._set_menu_open(False)
        self._close_timer.stop()

    def _on_close_timer(self) -> None:
        self._close()
