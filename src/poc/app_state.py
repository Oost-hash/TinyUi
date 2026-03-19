from PySide6.QtCore import QObject, Signal


class AppState(QObject):
    titleChanged = Signal()
    active_tab_changed = Signal(str)

    def __init__(self):
        super().__init__()
        self._title = ""
        self._active_tab = None

    @property
    def title(self):
        return self._title

    def set_title(self, value: str):
        if self._title != value:
            self._title = value
            self.titleChanged.emit()

    @property
    def active_tab(self):
        return self._active_tab

    def set_active_tab(self, tab_id: str):
        if self._active_tab != tab_id:
            self._active_tab = tab_id
            self.active_tab_changed.emit(tab_id)
