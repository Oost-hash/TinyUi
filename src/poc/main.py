import sys

from app_state import AppState
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)

    state = AppState()
    window = MainWindow(state)

    window.resize(800, 600)
    window.show()

    sys.exit(app.exec())
