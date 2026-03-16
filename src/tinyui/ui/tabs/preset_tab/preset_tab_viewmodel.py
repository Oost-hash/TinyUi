#  TinyUI - A mod for TinyPedal
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
#  licensed under GPLv3. TinyPedal is included as a submodule.

# tinyui/ui/tabs/preset_tab/preset_tab_viewmodel.py
from PySide6.QtCore import QObject, Signal


class PresetTabViewModel(QObject):
    """
    ViewModel voor Preset tab.
    """

    # Signals voor UI updates
    data_changed = Signal()

    def __init__(self):
        super().__init__()
        # TODO: Initialiseer preset data

    def refresh(self):
        """Refresh preset data"""
        # TODO: Laad presets
        self.data_changed.emit()
