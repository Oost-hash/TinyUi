from PySide6.QtWidgets import QTabWidget, QVBoxLayout, QWidget

from .tab_viewmodel import TabViewModel


class TabComponent(QWidget):
    """Rendert tabs via TabViewModel. Bezit lazy View instanties en index map."""

    def __init__(self, viewmodel: TabViewModel, parent=None):
        super().__init__(parent)
        self._vm = viewmodel
        self._views = {}          # tab_id -> QWidget (lazy)
        self._tab_index = {}      # tab_id -> int (O(1))
        self._index_to_tab = {}   # int -> tab_id (O(1) reverse)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self._tabs = QTabWidget()
        layout.addWidget(self._tabs)

        self._tabs.currentChanged.connect(self._on_tab_changed)
        self._vm.tabs_changed.connect(self._rebuild)
        self._vm.tab_activated.connect(self._on_activated)

        if self._vm.get_tab_ids():
            self._rebuild()

    # ── Opbouw ───────────────────────────────────────────────────────────────

    def _rebuild(self):
        self._tabs.blockSignals(True)
        while self._tabs.count():
            self._tabs.removeTab(0)
        self._tab_index.clear()
        self._index_to_tab.clear()

        for i, tab_id in enumerate(self._vm.get_tab_ids()):
            spec = self._vm.model.get_spec(tab_id)
            placeholder = self._views.get(tab_id) or QWidget()
            self._tabs.addTab(placeholder, spec.name)
            self._tab_index[tab_id] = i
            self._index_to_tab[i] = tab_id

        self._tabs.blockSignals(False)

        active = self._vm.get_active_tab()
        if active:
            self._on_activated(active, "")

    # ── Event handlers ───────────────────────────────────────────────────────

    def _on_tab_changed(self, index: int):
        """Gebruiker klikt op tab → VM activeren."""
        tab_id = self._index_to_tab.get(index)
        if tab_id:
            self._vm.activate(tab_id)

    def _on_activated(self, new_id: str, old_id: str):
        """VM heeft tab gewisseld → view lazy aanmaken, UI sync."""
        if new_id not in self._views:
            spec = self._vm.model.get_spec(new_id)
            vm = self._vm.get_viewmodel(new_id)
            if vm is None:
                return

            view = spec.view_class(vm)
            self._views[new_id] = view

            index = self._tab_index.get(new_id)
            if index is None:
                return

            self._tabs.blockSignals(True)
            self._tabs.removeTab(index)
            self._tabs.insertTab(index, view, spec.name)
            self._tab_index[new_id] = index
            self._index_to_tab[index] = new_id
            self._tabs.blockSignals(False)

        index = self._tab_index.get(new_id)
        if index is not None and self._tabs.currentIndex() != index:
            self._tabs.blockSignals(True)
            self._tabs.setCurrentIndex(index)
            self._tabs.blockSignals(False)
