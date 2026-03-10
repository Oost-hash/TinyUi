# tinyui/ui/components/tab_viewmodel.py
from PySide2.QtCore import QObject, Signal

from .tab_model import TabModel, TabSpec


class TabViewModel(QObject):
    """
    ViewModel voor TabComponent.
    Net zoals EditorViewModel voor TableEditor.

    Verbindt TabModel met UI via signals.
    """

    # Signals voor UI updates
    tabs_changed = Signal()  # Tab lijst gewijzigd
    tab_activated = Signal(str, str)  # (new_id, old_id)
    tab_registered = Signal(str)  # (tab_id)
    tab_unregistered = Signal(str)  # (tab_id)

    def __init__(self, model: TabModel = None):
        super().__init__()
        self._model = model or TabModel()

        # Subscribe naar model changes
        self._model.subscribe(self._on_model_change)

    # ========== Properties ==========

    @property
    def model(self) -> TabModel:
        return self._model

    def get_active_tab(self) -> str:
        return self._model.get_active_id() or ""

    def get_tab_ids(self) -> list:
        return self._model.get_all_ids()

    # ========== Commands ==========

    def register(self, spec: TabSpec):
        """Registreer nieuwe tab"""
        self._model.register(spec)
        return self  # chainable

    def build(self):
        """Finalize registratie, bouw ViewModels"""
        self._model.build()
        return self

    def activate(self, tab_id: str) -> bool:
        """Activeer specifieke tab"""
        return self._model.set_active(tab_id)

    def get_or_create_view(self, tab_id: str, parent=None):
        """Lazy view creatie"""
        return self._model.create_view(tab_id, parent)

    def get_viewmodel(self, tab_id: str):
        """Haal ViewModel van specifieke tab"""
        return self._model.get_viewmodel(tab_id)

    # ========== Private ==========

    def _on_model_change(self, event_type: str, data, extra):
        """Callback van TabModel"""
        if event_type == "registered":
            self.tab_registered.emit(data)
            self.tabs_changed.emit()
        elif event_type == "unregistered":
            self.tab_unregistered.emit(data)
            self.tabs_changed.emit()
        elif event_type == "activated":
            self.tab_activated.emit(data, extra)
