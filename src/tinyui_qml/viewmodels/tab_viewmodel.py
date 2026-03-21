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

from PySide6.QtCore import Property, QObject, Signal, Slot


class TabViewModel(QObject):
    currentIndexChanged = Signal()
    tabNamesChanged = Signal()

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._ids: list[str] = []
        self._names: list[str] = []
        self._icons: list[str] = []
        self._current_index: int = 0

    def register(self, tab_id: str, name: str, icon: str = "") -> None:
        self._ids.append(tab_id)
        self._names.append(name)
        self._icons.append(icon)
        self.tabNamesChanged.emit()

    # ── Properties ────────────────────────────────────────────────────────────

    @Property("QVariantList", notify=tabNamesChanged)
    def tabNames(self) -> list[str]:
        return self._names

    @Property("QVariantList", notify=tabNamesChanged)
    def tabIcons(self) -> list[str]:
        return self._icons

    @Property(int, notify=currentIndexChanged)
    def currentIndex(self) -> int:
        return self._current_index

    @Property(str, notify=currentIndexChanged)
    def currentTabId(self) -> str:
        if not self._ids:
            return ""
        return self._ids[self._current_index]

    @Property(str, notify=currentIndexChanged)
    def currentTabTitle(self) -> str:
        if not self._names:
            return ""
        return self._names[self._current_index]

    # ── Slots ─────────────────────────────────────────────────────────────────

    @Slot(int)
    def setCurrentIndex(self, index: int) -> None:
        if index < 0 or index >= len(self._ids):
            return
        if self._current_index == index:
            return
        self._current_index = index
        self.currentIndexChanged.emit()

    @Slot(str)
    def setCurrentById(self, tab_id: str) -> None:
        """Navigeer naar tab op id — handig voor acties vanuit menus."""
        if tab_id in self._ids:
            self.setCurrentIndex(self._ids.index(tab_id))
