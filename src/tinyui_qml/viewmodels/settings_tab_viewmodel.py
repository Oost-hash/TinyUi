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


class SettingsTabViewModel(QObject):
    darkModeChanged = Signal()

    def __init__(self, theme, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._theme = theme
        self._dark_mode = True

    @Property(bool, notify=darkModeChanged)
    def darkMode(self) -> bool:
        return self._dark_mode

    @Slot(bool)
    def setDarkMode(self, value: bool) -> None:
        if self._dark_mode != value:
            self._dark_mode = value
            self._theme.load("dark" if value else "light")
            self.darkModeChanged.emit()
