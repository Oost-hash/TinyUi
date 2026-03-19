from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Type

from PySide6.QtCore import QObject
from PySide6.QtWidgets import QWidget


@dataclass
class TabSpec:
    id: str
    name: str
    view_class: Type[QWidget]
    viewmodel_class: Type[QObject]
    icon: Optional[str] = None
    closable: bool = False
    enabled: bool = True
    order: int = 0
    on_activate: Optional[Callable] = None
    on_deactivate: Optional[Callable] = None


class TabModel:
    """Pure Python data container voor tabs. Geen instanties, geen Qt."""

    def __init__(self):
        self._tabs: Dict[str, TabSpec] = {}
        self._order: List[str] = []
        self._active_id: Optional[str] = None
        self._listeners: List[Callable] = []

    # ── Observable ──────────────────────────────────────────────────────────

    def subscribe(self, callback: Callable[[str, object, object], None]):
        self._listeners.append(callback)

    def _notify(self, event_type: str, data=None, extra=None):
        for listener in self._listeners:
            listener(event_type, data, extra)

    # ── Registratie ──────────────────────────────────────────────────────────

    def register(self, spec: TabSpec) -> "TabModel":
        if spec.id in self._tabs:
            raise ValueError(f"Tab '{spec.id}' is al geregistreerd")

        self._tabs[spec.id] = spec
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

    # ── Lifecycle ────────────────────────────────────────────────────────────

    def build(self) -> "TabModel":
        """Activeer de eerste tab. Maakt geen instanties aan."""
        if self._order and self._active_id is None:
            self.set_active(self._order[0])
        self._notify("built", list(self._order), None)
        return self

    # ── State ────────────────────────────────────────────────────────────────

    def set_active(self, tab_id: str) -> bool:
        if tab_id not in self._tabs:
            return False
        if tab_id == self._active_id:
            return False  # geen change, geen event

        old_id = self._active_id
        self._active_id = tab_id

        if old_id and old_id in self._tabs:
            spec_old = self._tabs[old_id]
            if spec_old.on_deactivate:
                spec_old.on_deactivate()

        spec_new = self._tabs[tab_id]
        if spec_new.on_activate:
            spec_new.on_activate()

        self._notify("activated", tab_id, old_id)
        return True

    # ── Queries ──────────────────────────────────────────────────────────────

    def get_spec(self, tab_id: str) -> Optional[TabSpec]:
        return self._tabs.get(tab_id)

    def get_active_id(self) -> Optional[str]:
        return self._active_id

    def get_all_ids(self) -> List[str]:
        return self._order.copy()

    def is_registered(self, tab_id: str) -> bool:
        return tab_id in self._tabs
