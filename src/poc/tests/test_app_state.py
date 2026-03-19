# tests/test_app_state.py

import pytest

from poc.app_state import AppState


def test_initial_state():
    state = AppState()

    assert state.page == "home"
    assert state.title == "Home"


def test_set_page_updates_state(qtbot):
    state = AppState()

    with qtbot.waitSignal(state.pageChanged):
        state.page = "settings"

    assert state.page == "settings"


def test_set_title_updates_state(qtbot):
    state = AppState()

    with qtbot.waitSignal(state.titleChanged):
        state.title = "Settings"

    assert state.title == "Settings"


def test_go_settings_command(qtbot):
    state = AppState()

    with qtbot.waitSignals([state.pageChanged, state.titleChanged]):
        state.go_settings()

    assert state.page == "settings"
    assert state.title == "Settings"


def test_no_signal_on_same_value(qtbot):
    state = AppState()

    with qtbot.assertNotEmitted(state.pageChanged):
        state.page = "home"  # zelfde waarde


def test_multiple_state_changes(qtbot):
    state = AppState()

    with qtbot.waitSignal(state.pageChanged):
        state.page = "settings"

    with qtbot.waitSignal(state.pageChanged):
        state.page = "home"

    assert state.page == "home"
