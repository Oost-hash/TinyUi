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

# tinyui/ui/components/tab_component.py
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTabBar, QTabWidget, QVBoxLayout, QWidget

from .tab_model import TabSpec
from .tab_viewmodel import TabViewModel


class TabComponent(QWidget):
    """
    Generieke tab component voor TinyUI.
    Net zoals TableEditor voor tabellen.

    Werkt met TabViewModel voor alle logica.
    Rendert tabs volgens TabSpec.
    """

    def __init__(
        self,
        viewmodel: TabViewModel,
        parent=None,
        tab_position: str = "north",  # north, south, west, east
        movable: bool = False,
        closable: bool = False,
    ):
        super().__init__(parent)

        self._vm = viewmodel
        self._closable = closable

        self._setup_appearance(tab_position, movable)
        self._connect_signals()

        # Build als er al tabs geregistreerd zijn
        if self._vm.get_tab_ids():
            self.rebuild_tabs()

    def _setup_appearance(self, tab_position: str, movable: bool):
        """Configureer tab look & feel"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._tabs = QTabWidget()

        # Tab positie
        positions = {
            "north": QTabWidget.North,
            "south": QTabWidget.South,
            "west": QTabWidget.West,
            "east": QTabWidget.East,
        }
        self._tabs.setTabPosition(positions.get(tab_position, QTabWidget.North))

        self._tabs.setMovable(movable)
        self._tabs.setTabsClosable(self._closable)

        # Signalen
        self._tabs.currentChanged.connect(self._on_tab_changed)
        if self._closable:
            self._tabs.tabCloseRequested.connect(self._on_tab_close)

        layout.addWidget(self._tabs)

    def _connect_signals(self):
        """Connect ViewModel signals"""
        self._vm.tabs_changed.connect(self.rebuild_tabs)
        self._vm.tab_activated.connect(self._on_vm_tab_activated)

    # ========== Data Binding ==========

    def rebuild_tabs(self):
        """(Re)build alle tabs vanuit ViewModel"""
        # Bewaar huidige index
        current_id = self._vm.get_active_tab()

        # Clear bestaande
        while self._tabs.count() > 0:
            self._tabs.removeTab(0)

        # Bouw nieuwe
        for tab_id in self._vm.get_tab_ids():
            spec = self._vm.model.get_spec(tab_id)
            if not spec:
                continue

            # Maak view (lazy)
            view = self._vm.get_or_create_view(tab_id, self)
            if not view:
                continue

            # Voeg toe
            index = self._tabs.addTab(view, spec.name)

            # Tab properties
            if spec.icon:
                # TODO: Icon loading
                pass

            self._tabs.setTabEnabled(index, spec.enabled)

        # Herstel actieve tab
        if current_id:
            self._activate_tab_by_id(current_id)

    def _activate_tab_by_id(self, tab_id: str):
        """Activeer tab op basis van ID"""
        for i in range(self._tabs.count()):
            # We matchen op view instance
            view = self._vm.get_or_create_view(tab_id)
            if self._tabs.widget(i) == view:
                self._tabs.setCurrentIndex(i)
                break

    def _get_tab_id_at_index(self, index: int) -> str:
        """Haal tab_id op basis van QTabWidget index"""
        widget = self._tabs.widget(index)
        if not widget:
            return ""

        # Zoek bijbehorende tab_id
        for tab_id in self._vm.get_tab_ids():
            if self._vm.get_or_create_view(tab_id) == widget:
                return tab_id
        return ""

    # ========== Event Handlers ==========

    def _on_tab_changed(self, index: int):
        """User heeft tab gewisseld via UI"""
        tab_id = self._get_tab_id_at_index(index)
        if tab_id:
            # Alleen sync naar VM, niet rebuild!
            self._vm.activate(tab_id)

    def _on_vm_tab_activated(self, new_id: str, old_id: str):
        """ViewModel heeft tab gewisseld"""
        self._activate_tab_by_id(new_id)

    def _on_tab_close(self, index: int):
        """User wil tab sluiten"""
        if not self._closable:
            return

        tab_id = self._get_tab_id_at_index(index)
        if tab_id:
            spec = self._vm.model.get_spec(tab_id)
            if spec and spec.closable:
                # TODO: Sluit logica via VM
                pass

    # ========== Public API ==========

    def get_tab_view(self, tab_id: str):
        """Haal specifieke tab view op"""
        return self._vm.get_or_create_view(tab_id)

    def get_tab_viewmodel(self, tab_id: str):
        """Haal specifieke tab ViewModel op"""
        return self._vm.get_viewmodel(tab_id)
