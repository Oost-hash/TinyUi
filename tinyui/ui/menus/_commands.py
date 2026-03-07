#
#  TinyUi - Menu Commands
#  Copyright (C) 2025 Oost-hash
#

"""Shared menu command functions."""

from tinyui.backend.controls import api, app_signal, loader


def menu_reload_preset():
    """Command - full reload"""
    loader.reload(reload_preset=True)
    app_signal.refresh.emit(True)


def menu_reload_only():
    """Command - fast reload"""
    loader.reload(reload_preset=False)
    app_signal.refresh.emit(True)


def menu_refresh_only():
    """Command - refresh GUI"""
    app_signal.refresh.emit(True)


def menu_restart_api():
    """Command - restart api"""
    api.restart()
    app_signal.refresh.emit(True)
