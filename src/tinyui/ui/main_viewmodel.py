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
