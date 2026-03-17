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

# tinyui/ui/components/tab_model.py
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Type


@dataclass
class TabSpec:
    """
    DSL: Definieer hoe één tab eruit ziet en werkt.
    Net zoals ColumnSpec voor TableEditor.
    """

    id: str  # Unieke identifier
    name: str  # Weergave naam
    view_class: Type  # De View class (bijv. ModuleTabView)
    viewmodel_class: Type  # De ViewModel class
    icon: Optional[str] = None  # Icon naam/path
    closable: bool = False  # Kan de tab gesloten worden?
    enabled: bool = True  # Is de tab actief?
    order: int = 0  # Volgorde in tabbar

    # Data die meegegeven wordt bij creatie
    context: Dict[str, Any] = field(default_factory=dict)

    # Lifecycle callbacks
    on_activate: Optional[Callable] = None
    on_deactivate: Optional[Callable] = None


class TabModel:
    """
    Observable data container voor tabs.
    Net zoals TableModel voor TableEditor.
    """

    def __init__(self):
        self._tabs: Dict[str, TabSpec] = {}
        self._order: List[str] = []
        self._active_id: Optional[str] = None
        self._listeners: List[Callable] = []

        # Instanties (worden lazy geladen)
        self._viewmodels: Dict[str, Any] = {}
        self._views: Dict[str, Any] = {}

    # ========== Observable Pattern ==========

    def subscribe(self, callback: Callable[[str, Any, Any], None]):
        """Callback(event_type, data, extra)"""
        self._listeners.append(callback)

    def _notify(self, event_type: str, data: Any = None, extra: Any = None):
        for listener in self._listeners:
            listener(event_type, data, extra)

    # ========== Tab Registratie ==========

    def register(self, spec: TabSpec) -> "TabModel":
        """
        Registreer een nieuwe tab definitie.
        Chainable: model.register().register().build()
        """
        if spec.id in self._tabs:
            raise ValueError(f"Tab '{spec.id}' is al geregistreerd")

        self._tabs[spec.id] = spec
        # Insert op juiste positie gebaseerd op order
        inserted = False
        for i, existing_id in enumerate(self._order):
            if self._tabs[existing_id].order > spec.order:
                self._order.insert(i, spec.id)
                inserted = True
                break
        if not inserted:
            self._order.append(spec.id)

        self._notify("registered", spec.id, spec)
        return self

    def unregister(self, tab_id: str) -> bool:
        """Verwijder een tab"""
        if tab_id not in self._tabs:
            return False

        # Cleanup instanties
        if tab_id in self._views:
            del self._views[tab_id]
        if tab_id in self._viewmodels:
            del self._viewmodels[tab_id]

        self._order.remove(tab_id)
        del self._tabs[tab_id]

        if self._active_id == tab_id:
            self._active_id = None

        self._notify("unregistered", tab_id, None)
        return True

    # ========== Lifecycle ==========

    def build(self):
        """Bouw alle geregistreerde tabs (instantieer ViewModels)"""
        for tab_id in self._order:
            spec = self._tabs[tab_id]
            # Maak ViewModel aan
            if tab_id not in self._viewmodels:
                try:
                    self._viewmodels[tab_id] = spec.viewmodel_class(**spec.context)
                except TypeError:
                    # Fallback: geen context argumenten
                    self._viewmodels[tab_id] = spec.viewmodel_class()

        self._notify("built", list(self._order), None)
        return self

    def create_view(self, tab_id: str, parent=None):
        """Maak View aan voor specifieke tab (lazy)"""
        if tab_id not in self._tabs:
            return None

        if tab_id not in self._views:
            spec = self._tabs[tab_id]
            viewmodel = self._viewmodels.get(tab_id)
            if viewmodel:
                self._views[tab_id] = spec.view_class(viewmodel, parent)
            else:
                self._views[tab_id] = spec.view_class(parent)

        return self._views[tab_id]

    # ========== State Management ==========

    def set_active(self, tab_id: str) -> bool:
        """Wissel naar andere tab"""
        if tab_id not in self._tabs:
            return False

        old_id = self._active_id
        self._active_id = tab_id

        # Lifecycle callbacks
        if old_id and old_id in self._tabs:
            spec_old = self._tabs[old_id]
            if spec_old.on_deactivate:
                spec_old.on_deactivate()

        spec_new = self._tabs[tab_id]
        if spec_new.on_activate:
            spec_new.on_activate()

        self._notify("activated", tab_id, old_id)
        return True

    # ========== Queries ==========

    def get_spec(self, tab_id: str) -> Optional[TabSpec]:
        return self._tabs.get(tab_id)

    def get_viewmodel(self, tab_id: str):
        return self._viewmodels.get(tab_id)

    def get_view(self, tab_id: str):
        return self._views.get(tab_id)

    def get_all_ids(self) -> List[str]:
        return self._order.copy()

    def get_active_id(self) -> Optional[str]:
        return self._active_id

    def is_registered(self, tab_id: str) -> bool:
        return tab_id in self._tabs
