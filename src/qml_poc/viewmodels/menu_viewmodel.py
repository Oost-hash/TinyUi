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

import logging

from PySide6.QtCore import QObject, Property, Signal, Slot, QTimer

log = logging.getLogger(__name__)


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

    def _dbg(self, action: str, **extra) -> None:
        state = (
            f"menuOpen={self._menu_open} "
            f"active={self._active_popup!r} "
            f"dismissed={self._dismissed!r} "
            f"blocked={self._blocked!r}"
        )
        detail = "  ".join(f"{k}={v!r}" for k, v in extra.items())
        log.debug("[menu] %-20s  %s  %s", action, state, detail)

    @Slot()
    def toggleMenu(self):
        """Hamburger-knop of TinyUi-tekst geklikt."""
        self._dbg("toggleMenu")
        if self._menu_open:
            self._close()
        else:
            self._set_menu_open(True)
            self._set_dropdown_open(True)   # hamburger geopend → dropdown zichtbaar
        self._close_timer.stop()

    @Slot()
    def closeMenu(self):
        """Sluit menu en alle popups (bijv. na Settings navigatie)."""
        self._dbg("closeMenu")
        self._close()

    @Slot(str)
    def hoverPopup(self, name: str):
        """Muis beweegt over een menu-knop — open als niet dismissed of geblokkeerd."""
        blocked = not self._menu_open or self._dismissed == name or self._blocked == name
        self._dbg("hoverPopup", name=name, blocked=blocked)
        if not blocked:
            self._set_active(name)
            self._set_dropdown_open(False)  # popup opent via hover → dropdown verbergen

    @Slot(str)
    def clickPopup(self, name: str):
        """Klik op een menu-knop — toggle; expliciete klik reset dismiss."""
        self._dbg("clickPopup", name=name)
        if self._active_popup == name:
            self._dismissed = name
            self._set_active("")
            self._set_dropdown_open(False)  # dismiss → dropdown blijft dicht
        else:
            self._dismissed = ""
            self._set_active(name)
            self._set_dropdown_open(False)  # popup opent → dropdown verbergen

    @Slot()
    def closeActivePopup(self):
        """Sluit huidige popup zonder dismiss (bijv. hover terug naar hamburger)."""
        self._dbg("closeActivePopup")
        self._set_active("")
        self._set_dropdown_open(True)   # hover terug naar hamburger → dropdown weer zichtbaar

    @Slot()
    def dismissActivePopup(self):
        """Klik buiten een popup — sluit popup, start timer, menu blijft open."""
        self._dbg("dismissActivePopup")
        if self._active_popup:
            self._dismissed = self._active_popup
            self._set_active("")
            self._set_dropdown_open(False)
            if self._menu_open:
                self._close_timer.start()

    @Slot()
    def mouseEnteredMenu(self):
        """Muis is in de menu-zone — stop auto-close timer."""
        self._dbg("mouseEnteredMenu")
        self._close_timer.stop()

    @Slot()
    def mouseLeftMenu(self):
        """Muis verlaat de menu-zone — start auto-close timer."""
        self._dbg("mouseLeftMenu")
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
            log.debug("[menu] _set_active  %r → %r", prev, name)
            self.activePopupChanged.emit()
            if name:
                self._close_timer.stop()
            if prev:
                self._blocked = prev
                log.debug("[menu] blocking %r for 100ms", prev)
                QTimer.singleShot(100, lambda p=prev: self._unblock(p))

    def _unblock(self, name: str) -> None:
        if self._blocked == name:
            log.debug("[menu] unblocked %r", name)
            self._blocked = ""

    def _close(self) -> None:
        """Sluit alles en reset alle state voor de volgende sessie."""
        log.debug("[menu] _close")
        self._dismissed = ""
        self._blocked = ""
        self._set_active("")
        self._set_dropdown_open(False)
        self._set_menu_open(False)
        self._close_timer.stop()

    def _on_close_timer(self) -> None:
        self._close()
