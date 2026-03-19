import pytest
from PySide6.QtWidgets import QApplication

from poc.app_state import AppState


# ✅ Zorg dat er altijd een QApplication is
@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


# ✅ Centrale AppState fixture
@pytest.fixture
def state(qapp):
    return AppState()


# ✅ Helper: meerdere signals wachten (optioneel)
@pytest.fixture
def wait_signals(qtbot):
    def _wait(signals):
        return qtbot.waitSignals(signals)

    return _wait
