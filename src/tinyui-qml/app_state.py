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


class AppState(QObject):
    titleChanged = Signal()
    activeTabChanged = Signal(str)

    def __init__(self):
        super().__init__()
        self._title = ""
        self._active_tab = ""

    @Property(str, notify=titleChanged)
    def title(self):
        return self._title

    @Slot(str)
    def setTitle(self, value: str):
        if self._title != value:
            self._title = value
            self.titleChanged.emit()

    @Property(str, notify=activeTabChanged)
    def activeTab(self):
        return self._active_tab

    @Slot(str)
    def setActiveTab(self, tab_id: str):
        if self._active_tab != tab_id:
            self._active_tab = tab_id
            self.activeTabChanged.emit(tab_id)
