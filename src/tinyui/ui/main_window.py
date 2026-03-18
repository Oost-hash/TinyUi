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

# tinyui/ui/main_window.py

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QColor, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from tinyui.const import APP_NAME, VERSION
from tinyui.ui.components.frameless_window import FramelessWindow
from tinyui.ui.main_viewmodel import MainViewModel


class MainWindow(FramelessWindow):
    """
    Hoofdvenster van TinyUI.
    Erft van FramelessWindow en bouwt de menubalk en tabs zelf op.
    """

    def __init__(self, viewmodel: MainViewModel):
        super().__init__(
            title=f"{APP_NAME} v{VERSION}",
            closable=True,
            minimizable=True,
            maximizable=True,
            icon=QApplication.instance().windowIcon(),
        )
        self._vm = viewmodel
        self._vm.window_requested.connect(self._on_window_requested)

        # Bouw de menubalk
        self._build_menubar()

        # Bouw de inhoud (tabs)
        self._build_content()

        # Mouse tracking voor alle kinderen inschakelen
        self.enable_mouse_tracking_recursive()

        self.resize(1024, 768)
        self.setMinimumSize(700, 450)

    def _build_menubar(self):
        """Bouw de menubalk met File, plugin-menu's en Help."""
        menubar = self.menubar()  # wordt aangemaakt indien nodig

        # File menu
        file_menu = menubar.addMenu("&File")
        quit_action = QAction("&Quit", self)
        quit_action.setShortcut("Ctrl+Q")
        quit_action.triggered.connect(QApplication.quit)
        file_menu.addAction(quit_action)

        # Plugin menus — gegroepeerd per menu
        for menu_name, specs in self._vm.editor_groups.items():
            menu = menubar.addMenu(f"&{menu_name}")
            for spec in specs:
                action = QAction(spec.title, self)
                action.triggered.connect(
                    lambda checked=False, s=spec: self._vm.open_editor(s)
                )
                menu.addAction(action)

        # Help menu
        help_menu = menubar.addMenu("&Help")
        about_action = QAction(f"&About {APP_NAME}", self)
        about_action.triggered.connect(self._vm.show_about)
        help_menu.addAction(about_action)

    def _build_content(self):
        """Bouw de centrale inhoud: tabs met widgets en presets."""
        # We maken een eigen widget aan als container voor de tabs,
        # die we via set_content in FramelessWindow plaatsen.
        container = QWidget()

        layout = QVBoxLayout(container)
        # Marges van 8px om overlapping met afgeronde hoeken te voorkomen
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(0)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Tabs vullen
        self.tabs.addTab(self._build_widgets_tab(), "Widgets")
        self.tabs.addTab(QWidget(), "Presets")

        # Reload knop rechtsboven in de tabbalk
        reload_btn = QPushButton("Reload UI")
        reload_btn.setObjectName("reloadBtn")
        reload_btn.setProperty("compact", True)
        reload_btn.clicked.connect(self._reload_ui)
        self.tabs.setCornerWidget(reload_btn)

        # Stel de container in als inhoud van het venster
        self.set_content(container)

    def _build_widgets_tab(self) -> QWidget:
        """Maak het tabblad met de lijst van widgets."""
        scroll = QScrollArea()
        scroll.setObjectName("widgetList")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        container = QWidget()
        container.setObjectName("widgetListContainer")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        container.setAutoFillBackground(True)

        for i, spec in enumerate(self._vm.widget_specs):
            row = QFrame()
            row.setObjectName("widgetRow")
            row.setProperty("alt", i % 2 == 1)
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(8, 2, 8, 2)

            toggle = QCheckBox()
            toggle.setChecked(spec.enable)
            toggle.stateChanged.connect(
                lambda state, s=spec: self._vm.toggle_widget(s, state)
            )
            row_layout.addWidget(toggle)

            title = QLabel(spec.title)
            title.setObjectName("widgetTitle")
            title.setMinimumWidth(150)
            row_layout.addWidget(title)

            desc = QLabel(spec.description)
            desc.setObjectName("widgetDesc")
            row_layout.addWidget(desc, stretch=1)

            config_btn = QPushButton("Configure")
            config_btn.setObjectName("widgetConfigBtn")
            config_btn.setProperty("compact", True)
            config_btn.clicked.connect(
                lambda checked=False, s=spec: self._vm.configure_widget(s)
            )
            row_layout.addWidget(config_btn)

            layout.addWidget(row)

        layout.addStretch()
        scroll.setWidget(container)
        return scroll

    def _reload_ui(self):
        from tinyui.themes.style import load_theme

        self.setStyleSheet(load_theme("dark"))

    # --- Window request handling ---

    def _on_window_requested(self, window_type, params):
        handler = self._window_handlers.get(window_type)
        if handler:
            handler(self, params)

    def _open_about(self, _params):
        QMessageBox.about(
            self,
            f"About {APP_NAME}",
            f"{APP_NAME} v{VERSION}\n\nA modular overlay — just input data.",
        )

    def _open_widget_config(self, spec):
        QMessageBox.information(
            self,
            spec.title,
            f"Widget config for '{spec.title}' is still under construction.",
        )

    def _open_editor(self, spec):
        from tinyui.ui.editors.data_editor_dialog import DataEditorDialog

        editor = DataEditorDialog(self._vm.core, spec)
        self._vm.register_window(spec.id, editor)
        editor.show()

    _window_handlers = {
        "about": _open_about,
        "widget_config": _open_widget_config,
        "editor": _open_editor,
    }

    def closeEvent(self, event):
        QApplication.quit()
        event.accept()
