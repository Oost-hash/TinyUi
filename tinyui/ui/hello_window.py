from PySide2 import QtCore
from PySide2.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from tinyui.adapters import cfg, lifecycle

from .editors.heatmap import HeatmapEditor


class HelloWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TinyUi - Hello")

        # Test: icon info
        icon = self.windowIcon()
        print(f"[ICON TEST] IsNull: {icon.isNull()}")
        print(f"[ICON TEST] Size: {icon.actualSize(QtCore.QSize(64, 64))}")
        print(f"[ICON TEST] Available sizes: {icon.availableSizes()}")

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        api_name = cfg.api_name
        label = QLabel(f"Hallo! API = {api_name}")
        layout.addWidget(label)

        # Knop om HeatmapEditor te openen
        self.open_heatmap_btn = QPushButton("Open Heatmap Editor")
        self.open_heatmap_btn.clicked.connect(self.open_heatmap_editor)
        layout.addWidget(self.open_heatmap_btn)

        # Afsluitknop
        quit_btn = QPushButton("Close")
        quit_btn.clicked.connect(self._quit)
        layout.addWidget(quit_btn)

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
        from tinyui.adapters import lifecycle

        lifecycle.close()  # Stop TinyPedal
        QApplication.quit()  # Stop Qt
