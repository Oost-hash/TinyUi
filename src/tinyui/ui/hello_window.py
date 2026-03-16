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

from collections import defaultdict

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from tinycore import App
from tinyui.const import APP_NAME, VERSION


class HelloWindow(QMainWindow):
    def __init__(self, core: App):
        super().__init__()
        self._core = core
        self._open_editors: dict[str, QWidget] = {}
        self.setWindowTitle(f"{APP_NAME} v{VERSION}")
        self.resize(1024, 768)

        self._build_menubar()
        self._build_tabs()

    def _build_menubar(self):
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")
        quit_action = QAction("&Quit", self)
        quit_action.setShortcut("Ctrl+Q")
        quit_action.triggered.connect(QApplication.quit)
        file_menu.addAction(quit_action)

        # Plugin menus — grouped by spec.menu
        grouped: dict[str, list] = defaultdict(list)
        for spec in self._core.editors.all():
            menu_name = spec.menu or "Tools"
            grouped[menu_name].append(spec)

        for menu_name, specs in grouped.items():
            menu = menubar.addMenu(f"&{menu_name}")
            for spec in specs:
                action = QAction(spec.title, self)
                action.triggered.connect(
                    lambda checked=False, s=spec: self._open_editor(s)
                )
                menu.addAction(action)

        # Help menu
        help_menu = menubar.addMenu("&Help")
        about_action = QAction(f"&About {APP_NAME}", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _build_tabs(self):
        tabs = QTabWidget()
        self.setCentralWidget(tabs)

        tabs.addTab(self._build_widgets_tab(), "Widgets")

    def _build_widgets_tab(self):
        from PySide6.QtWidgets import QFrame, QScrollArea

        scroll = QScrollArea()
        scroll.setObjectName("widgetList")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        container = QWidget()
        container.setObjectName("widgetListContainer")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        for i, spec in enumerate(self._core.widgets.all()):
            row = QFrame()
            row.setObjectName("widgetRow")
            row.setProperty("alt", i % 2 == 1)
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(8, 6, 8, 6)

            toggle = QCheckBox()
            toggle.setChecked(spec.enable)
            toggle.stateChanged.connect(
                lambda state, s=spec: self._toggle_widget(s, state)
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
            config_btn.clicked.connect(
                lambda checked=False, s=spec: self._configure_widget(s)
            )
            row_layout.addWidget(config_btn)

            layout.addWidget(row)

        layout.addStretch()
        scroll.setWidget(container)
        return scroll

    def _toggle_widget(self, spec, state):
        spec.enable = bool(state)

    def _configure_widget(self, spec):
        QMessageBox.information(
            self,
            spec.title,
            f"Widget config for '{spec.title}' is still under construction.",
        )

    def _open_editor(self, spec):
        from tinyui.ui.editors.data_editor_dialog import DataEditorDialog

        existing = self._open_editors.get(spec.id)
        if existing is not None and existing.isVisible():
            existing.raise_()
            existing.activateWindow()
            return

        editor = DataEditorDialog(self._core, spec)
        self._open_editors[spec.id] = editor
        editor.show()

    def _show_about(self):
        QMessageBox.about(
            self,
            f"About {APP_NAME}",
            f"{APP_NAME} v{VERSION}\n\nA modular overlay — just input data.",
        )

    def closeEvent(self, event):
        QApplication.quit()
        event.accept()
