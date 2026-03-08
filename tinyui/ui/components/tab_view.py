#
#  TinyUi - Tab View
#  Copyright (C) 2026 Oost-hash
#

"""Tab view component."""

from PySide2.QtWidgets import QTabWidget, QVBoxLayout, QWidget

from tinyui.backend.controls import app_signal, mctrl, wctrl
from tinyui.ui.panels.hotkey_view import HotkeyList
from tinyui.ui.panels.module_view import ModuleList
from tinyui.ui.panels.pace_notes_view import PaceNotesControl
from tinyui.ui.panels.preset_view import PresetList
from tinyui.ui.panels.spectate_view import SpectateList

from .notify_bar import NotifyBar

# Tab definitions: (label, factory)
# factory is a callable(parent) -> QWidget
TAB_DEFS = [
    ("Widget", lambda parent: ModuleList(parent, wctrl)),
    ("Module", lambda parent: ModuleList(parent, mctrl)),
    ("Preset", lambda parent: PresetList(parent)),
    ("Spectate", lambda parent: SpectateList(parent)),
    ("Pacenotes", lambda parent: PaceNotesControl(parent)),
    ("Hotkey", lambda parent: HotkeyList(parent)),
]


class TabView(QWidget):
    """Tab view"""

    def __init__(self, parent):
        super().__init__(parent)
        # Notify bar
        notify_bar = NotifyBar(self)

        # Build tabs from definitions
        self._tabs = QTabWidget(self)
        self._tab_index = {}
        for label, factory in TAB_DEFS:
            tab = factory(self)
            self._tabs.addTab(tab, label)
            self._tab_index[label] = self._tabs.count() - 1
            app_signal.refresh.connect(tab.refresh)
        self._tabs.currentChanged.connect(self.refresh)

        # Connect notify bar buttons to tabs
        notify_bar.presetlocked.clicked.connect(lambda: self.select_tab("Preset"))
        notify_bar.spectate.clicked.connect(lambda: self.select_tab("Spectate"))
        notify_bar.pacenotes.clicked.connect(lambda: self.select_tab("Pacenotes"))
        notify_bar.hotkey.clicked.connect(lambda: self.select_tab("Hotkey"))

        # Main view
        layout_main = QVBoxLayout()
        layout_main.setContentsMargins(0, 0, 0, 0)
        layout_main.setSpacing(0)
        layout_main.addWidget(self._tabs)
        layout_main.addWidget(notify_bar)
        self.setLayout(layout_main)

        # Connect app signal
        app_signal.updates.connect(notify_bar.updates.checking)
        app_signal.refresh.connect(notify_bar.refresh)

    def refresh(self):
        """Refresh tab area"""
        # Workaround to correct tab scroll area size after height changed
        width = self.width()
        height = self.height()
        self.resize(width, height - 1)
        self.resize(width, height + 1)

    def select_tab(self, label: str):
        """Select tab by label"""
        self._tabs.setCurrentIndex(self._tab_index[label])

    def select_preset_tab(self):
        """Select preset tab"""
        self.select_tab("Preset")
