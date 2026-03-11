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

from PySide2 import QtCore
from PySide2.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QVBoxLayout,
    QWidget,
)

from tinyui.adapters import cfg, lifecycle

from .components.button import Button, create_danger_button, create_primary_button
from .components.tabs import TabComponent, TabSpec, TabViewModel
from .editors import HeatmapEditor
from .tabs import ModuleTabView, ModuleTabViewModel, PresetTabView, PresetTabViewModel


class HelloWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TinyUI - Hello")
        self.resize(1024, 768)

        # Test: icon info
        icon = self.windowIcon()
        print(f"[ICON TEST] IsNull: {icon.isNull()}")
        print(f"[ICON TEST] Size: {icon.actualSize(QtCore.QSize(64, 64))}")
        print(f"[ICON TEST] Available sizes: {icon.availableSizes()}")

        # Centrale widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Info label
        api_name = cfg.api_name
        label = QLabel(f"Hallo! API = {api_name}")
        layout.addWidget(label)

        # === TAB COMPONENT ===
        # 1. Maak ViewModel
        self._tab_vm = TabViewModel()

        # 2. Registreer tabs (chainable)
        self._tab_vm.register(
            TabSpec(
                id="presets",
                name="Presets",
                view_class=PresetTabView,
                viewmodel_class=PresetTabViewModel,
                order=1,
            )
        ).register(
            TabSpec(
                id="modules",
                name="Modules",
                view_class=ModuleTabView,
                viewmodel_class=ModuleTabViewModel,
                order=2,
            )
        ).build()  # Finalize

        # 3. Maak View
        self._tabs = TabComponent(self._tab_vm, self)
        layout.addWidget(self._tabs)

        # 4. Activeer eerste tab
        self._tab_vm.activate("presets")

        # === BUTTONS ===
        buttons_layout = QHBoxLayout()

        # Primary button voor Heatmap Editor (met loading support)
        self.open_heatmap_btn = Button(
            "Open Heatmap Editor",
            variant=Button.PRIMARY,
            size=Button.MEDIUM,
            on_click=self.open_heatmap_editor,
        )
        buttons_layout.addWidget(self.open_heatmap_btn)

        # Ghost button voor secondary actie (bijvoorbeeld "Refresh")
        self.refresh_btn = Button(
            "Refresh",
            variant=Button.GHOST,
            size=Button.SMALL,
            on_click=self._on_refresh,
        )
        buttons_layout.addWidget(self.refresh_btn)

        # Spacer
        buttons_layout.addStretch()

        # Danger button voor afsluiten (rood = destructieve actie)
        self.quit_btn = create_danger_button("Close", on_click=self._quit, parent=self)
        buttons_layout.addWidget(self.quit_btn)

        layout.addLayout(buttons_layout)

        # Heatmap editor instance (voor single window gedrag)
        self.heatmap_editor = None

    def open_heatmap_editor(self):
        """Opent het HeatmapEditor-venster met loading state."""
        # Toon loading state op de button
        self.open_heatmap_btn.set_loading(True)

        # Simuleer async loading (of echt werk doen)
        QtCore.QTimer.singleShot(500, self._do_open_heatmap)

    def _do_open_heatmap(self):
        """Daadwerkelijk openen van editor."""
        self.open_heatmap_btn.set_loading(False)

        if self.heatmap_editor is None or not self.heatmap_editor.isVisible():
            self.heatmap_editor = HeatmapEditor()
            self.heatmap_editor.show()
        else:
            self.heatmap_editor.raise_()
            self.heatmap_editor.activateWindow()

    def _on_refresh(self):
        """Handler voor refresh button."""
        print("[HelloWindow] Refresh clicked")
        # Hier kun je data herladen, UI updaten, etc.
        self.refresh_btn.set_loading(True)
        QtCore.QTimer.singleShot(300, lambda: self.refresh_btn.set_loading(False))

    def closeEvent(self, event):
        """Overschrijf kruisje-gedrag: sluit hele applicatie."""
        self._quit()
        event.accept()

    def _quit(self):
        """Graceful shutdown."""
        lifecycle.close()  # Stop TinyPedal
        QApplication.quit()  # Stop Qt
