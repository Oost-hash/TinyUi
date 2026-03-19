from PySide6.QtCore import QObject, Signal

from .tab_model import TabModel, TabSpec


class TabViewModel(QObject):
    """Qt bridge voor TabModel. Bezit lazy ViewModel instanties."""

    tabs_changed = Signal()
    tab_activated = Signal(str, str)  # (new_id, old_id)
    tab_registered = Signal(str)
    tab_unregistered = Signal(str)

    def __init__(self, app_state, model: TabModel = None):
        super().__init__()
        self._app_state = app_state
        self._model = model or TabModel()
        self._viewmodels = {}

        self._model.subscribe(self._on_model_change)

    # ── Properties ───────────────────────────────────────────────────────────

    @property
    def model(self) -> TabModel:
        return self._model

    def get_active_tab(self) -> str:
        return self._model.get_active_id() or ""

    def get_tab_ids(self) -> list:
        return self._model.get_all_ids()

    def get_viewmodel(self, tab_id: str):
        return self._viewmodels.get(tab_id)

    # ── Commands ─────────────────────────────────────────────────────────────

    def register(self, spec: TabSpec) -> "TabViewModel":
        self._model.register(spec)
        return self

    def build(self) -> "TabViewModel":
        self._model.build()
        return self

    def activate(self, tab_id: str) -> bool:
        """Activeer tab. Maakt ViewModel lazy aan bij eerste activatie."""
        changed = self._model.set_active(tab_id)
        if not changed:
            return False

        if tab_id not in self._viewmodels:
            spec = self._model.get_spec(tab_id)
            self._viewmodels[tab_id] = spec.viewmodel_class(app_state=self._app_state)

        return True

    # ── Private ──────────────────────────────────────────────────────────────

    def _on_model_change(self, event_type: str, data, extra):
        if event_type == "registered":
            self.tab_registered.emit(data)
            self.tabs_changed.emit()
        elif event_type == "unregistered":
            self.tab_unregistered.emit(data)
            self.tabs_changed.emit()
        elif event_type == "activated":
            # ViewModel aanmaken als nog niet bestaat (bijv. via build())
            if data not in self._viewmodels:
                spec = self._model.get_spec(data)
                if spec:
                    self._viewmodels[data] = spec.viewmodel_class(
                        app_state=self._app_state
                    )
            self.tab_activated.emit(data, extra or "")
