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

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenuBar,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from tinyui.const import APP_NAME, VERSION
from tinyui.ui.components.title_bar import TitleBar
from tinyui.ui.main_viewmodel import MainViewModel


class MainView(QWidget):
    def __init__(self, viewmodel: MainViewModel):
        super().__init__()
        self._vm = viewmodel
        self.setObjectName("mainView")

        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        from PySide6.QtWidgets import QApplication

        self.title_bar = TitleBar(
            f"{APP_NAME} v{VERSION}",
            minimizable=True,
            icon=QApplication.instance().windowIcon(),
        )
        layout.addWidget(self.title_bar)

        self.menubar = QMenuBar()
        layout.addWidget(self.menubar)

        content = QVBoxLayout()
        content.setContentsMargins(5, 5, 5, 5)
        content.setSpacing(0)

        self.tabs = QTabWidget()
        content.addWidget(self.tabs)
        layout.addLayout(content)


_GRIP = 6  # pixels from edge for resize


class HelloWindow(QMainWindow):
    def __init__(self, viewmodel: MainViewModel):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setMouseTracking(True)
        self._vm = viewmodel
        self._resize_edge = None
        self.resize(1024, 768)

        self._vm.window_requested.connect(self._on_window_requested)

        self._build_ui()
        self._build_menubar()

    # --- Window dispatch ---

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

    # --- UI building ---

    def _build_menubar(self):
        menubar = self.main_view.menubar

        # File menu
        file_menu = menubar.addMenu("&File")
        quit_action = QAction("&Quit", self)
        quit_action.setShortcut("Ctrl+Q")
        quit_action.triggered.connect(QApplication.quit)
        file_menu.addAction(quit_action)

        # Plugin menus — grouped by spec.menu
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

    def _build_ui(self):
        self.main_view = MainView(self._vm)
        self.setCentralWidget(self.main_view)

        self.main_view.tabs.addTab(self._build_widgets_tab(), "Widgets")
        self.main_view.tabs.addTab(QWidget(), "Presets")

        reload_btn = QPushButton("Reload UI")
        reload_btn.setObjectName("reloadBtn")
        reload_btn.setProperty("compact", True)
        reload_btn.clicked.connect(self._reload_ui)
        self.main_view.tabs.setCornerWidget(reload_btn)

    def _reload_ui(self):
        from tinyui.themes.style import load_theme

        self.setStyleSheet(load_theme("dark"))

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

    # --- Edge resize ---

    def _edge_at(self, pos):
        r = self.rect()
        edges = Qt.Edges()
        if pos.x() < _GRIP:
            edges |= Qt.LeftEdge
        if pos.x() > r.width() - _GRIP:
            edges |= Qt.RightEdge
        if pos.y() < _GRIP:
            edges |= Qt.TopEdge
        if pos.y() > r.height() - _GRIP:
            edges |= Qt.BottomEdge
        return edges

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            edges = self._edge_at(event.position().toPoint())
            if edges:
                self.windowHandle().startSystemResize(edges)
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        edges = self._edge_at(event.position().toPoint())
        if edges == (Qt.LeftEdge | Qt.TopEdge) or edges == (
            Qt.RightEdge | Qt.BottomEdge
        ):
            self.setCursor(Qt.SizeFDiagCursor)
        elif edges == (Qt.RightEdge | Qt.TopEdge) or edges == (
            Qt.LeftEdge | Qt.BottomEdge
        ):
            self.setCursor(Qt.SizeBDiagCursor)
        elif edges & (Qt.LeftEdge | Qt.RightEdge):
            self.setCursor(Qt.SizeHorCursor)
        elif edges & (Qt.TopEdge | Qt.BottomEdge):
            self.setCursor(Qt.SizeVerCursor)
        else:
            self.setCursor(Qt.ArrowCursor)
        super().mouseMoveEvent(event)

    def closeEvent(self, event):
        QApplication.quit()
        event.accept()
