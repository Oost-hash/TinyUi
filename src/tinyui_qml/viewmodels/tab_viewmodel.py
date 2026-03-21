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

from PySide6.QtCore import QObject, Property, Signal, Slot


class TabViewModel(QObject):
    currentIndexChanged = Signal()
    tabNamesChanged = Signal()

    def __init__(self, app_state):
        super().__init__()
        self._app_state = app_state
        self._ids = []        # ordered list of tab ids
        self._names = []      # ordered list of tab names
        self._icons = []      # ordered list of Segoe Fluent Icons glyphs
        self._current_index = 0

    def register(self, tab_id: str, name: str, icon: str = ""):
        self._ids.append(tab_id)
        self._names.append(name)
        self._icons.append(icon)
        self.tabNamesChanged.emit()

    @Property("QVariantList", notify=tabNamesChanged)
    def tabNames(self):
        return self._names

    @Property("QVariantList", notify=tabNamesChanged)
    def tabIcons(self):
        return self._icons

    @Property(int, notify=currentIndexChanged)
    def currentIndex(self):
        return self._current_index

    @Slot(int)
    def setCurrentIndex(self, index: int):
        if index < 0 or index >= len(self._ids):
            return
        if self._current_index == index:
            return
        self._current_index = index
        tab_id = self._ids[index]
        self._app_state.setActiveTab(tab_id)
        self._app_state.setTitle(self._names[index])
        self.currentIndexChanged.emit()
