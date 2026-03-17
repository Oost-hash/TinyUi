from collections import defaultdict

from PySide6.QtCore import QObject, Signal

from tinycore import App


class MainViewModel(QObject):
    """ViewModel for the main window — owns all non-UI logic."""

    # (window_type: str, params: object)
    window_requested = Signal(str, object)

    def __init__(self, core: App):
        super().__init__()
        self._core = core
        self._open_windows: dict[str, object] = {}

    @property
    def widget_specs(self):
        return self._core.widgets.all()

    @property
    def editor_specs(self):
        return self._core.editors.all()

    @property
    def editor_groups(self) -> dict[str, list]:
        grouped: dict[str, list] = defaultdict(list)
        for spec in self.editor_specs:
            menu_name = spec.menu or "Tools"
            grouped[menu_name].append(spec)
        return grouped

    def toggle_widget(self, spec, state):
        spec.enable = bool(state)

    def show_about(self):
        self.window_requested.emit("about", None)

    def configure_widget(self, spec):
        self.window_requested.emit("widget_config", spec)

    def open_editor(self, spec):
        existing = self._open_windows.get(spec.id)
        if existing is not None and existing.isVisible():
            existing.raise_()
            existing.activateWindow()
            return
        self.window_requested.emit("editor", spec)

    def register_window(self, key, window):
        self._open_windows[key] = window

    @property
    def core(self):
        return self._core
