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

# tinyui/ui/tabs/preset_tab/preset_tab_view.py
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from .preset_tab_viewmodel import PresetTabViewModel


class PresetTabView(QWidget):
    """
    View voor Preset tab.
    """

    def __init__(self, viewmodel: PresetTabViewModel, parent=None):
        super().__init__(parent)
        self._vm = viewmodel

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        """Bouw UI"""
        layout = QVBoxLayout(self)

        # Placeholder
        label = QLabel("Preset Tab - TODO")
        layout.addWidget(label)

        # TODO: Voeg preset UI toe

    def _connect_signals(self):
        """Connect ViewModel signals"""
        self._vm.data_changed.connect(self._on_data_changed)

    def _on_data_changed(self):
        """Handle data changes"""
        # TODO: Update UI
        pass
