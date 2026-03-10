# hello_window.py
from PySide2 import QtCore
from PySide2.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from tinyui.adapters import cfg, lifecycle

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

        # Knop om HeatmapEditor te openen
        self.open_heatmap_btn = QPushButton("Open Heatmap Editor")
        self.open_heatmap_btn.clicked.connect(self.open_heatmap_editor)
        buttons_layout.addWidget(self.open_heatmap_btn)

        # Afsluitknop
        quit_btn = QPushButton("Close")
        quit_btn.clicked.connect(self._quit)
        buttons_layout.addWidget(quit_btn)

        layout.addLayout(buttons_layout)

        # Heatmap editor instance (voor single window gedrag)
        self.heatmap_editor = None

    def open_heatmap_editor(self):
        """Opent het HeatmapEditor-venster."""
        if self.heatmap_editor is None or not self.heatmap_editor.isVisible():
            self.heatmap_editor = HeatmapEditor()
            self.heatmap_editor.show()
        else:
            self.heatmap_editor.raise_()

    def closeEvent(self, event):
        """Overschrijf kruisje-gedrag: sluit hele applicatie."""
        self._quit()
        event.accept()

    def _quit(self):
        """Graceful shutdown."""
        lifecycle.close()  # Stop TinyPedal
        QApplication.quit()  # Stop Qt
