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

from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QMainWindow,
    QPushButton,
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

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Build editor buttons from registered EditorSpecs
        for spec in core.editors.all():
            btn = QPushButton(f"Open {spec.title}")
            btn.clicked.connect(lambda checked=False, s=spec: self._open_editor(s))
            layout.addWidget(btn)

        layout.addStretch()

        # Quit
        buttons = QHBoxLayout()
        buttons.addStretch()
        btn_quit = QPushButton("Quit")
        btn_quit.clicked.connect(QApplication.quit)
        buttons.addWidget(btn_quit)
        layout.addLayout(buttons)

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

    def closeEvent(self, event):
        QApplication.quit()
        event.accept()
