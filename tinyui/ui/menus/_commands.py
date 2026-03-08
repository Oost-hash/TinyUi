#
#  TinyUi - Menu Commands
#  Copyright (C) 2026 Oost-hash
#

"""Shared menu command functions."""

from tinyui.backend.controls import api, loader

from .. import _store as store


def menu_reload_preset():
    """Command - full reload"""
    loader.reload(reload_preset=True)
    store.refresh_ui()


def menu_reload_only():
    """Command - fast reload"""
    loader.reload(reload_preset=False)
    store.refresh_ui()


def menu_refresh_only():
    """Command - refresh GUI"""
    store.refresh_ui()


def menu_restart_api():
    """Command - restart api"""
    api.restart()
    store.refresh_ui()
