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

import logging
import os
import platform
import sys

# Logging vóór alle andere imports — configure() zet basicConfig in
from tinyui_qml import log as app_log

app_log.configure()

import PySide6
from PySide6.QtCore import QUrl, qVersion
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuick import QQuickWindow
from PySide6.QtQuickControls2 import QQuickStyle

from tinyui_qml.app_state import AppState
from tinyui_qml.const import APP_NAME, VERSION
from tinyui_qml.icons import Icons, glyph, load_font
from tinyui_qml.theme import Theme
from tinyui_qml.viewmodels.home_tab_viewmodel import HomeTabViewModel
from tinyui_qml.viewmodels.menu_viewmodel import MenuViewModel
from tinyui_qml.viewmodels.settings_tab_viewmodel import SettingsTabViewModel
from tinyui_qml.viewmodels.statusbar_viewmodel import StatusBarViewModel
from tinyui_qml.viewmodels.tab_viewmodel import TabViewModel


def main():
    QQuickWindow.setDefaultAlphaBuffer(
        True
    )  # vóór app — alpha-kanaal voor transparantie
    QQuickStyle.setStyle("Basic")
    app = QGuiApplication(sys.argv)
    load_font()
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(VERSION)

    log = logging.getLogger(__name__)
    log.info("── %s %s ──────────────────────────────", APP_NAME, VERSION)
    log.info("OS:      %s %s", platform.system(), platform.release())
    log.info("Python:  %s", platform.python_version())
    log.info("Qt:      %s  PySide6: %s", qVersion(), PySide6.__version__)
    log.info("Backend: %s", app.platformName())

    # Objecten op functie-niveau bewaren — outleven de engine
    state = AppState()
    theme = Theme()
    menu_vm = MenuViewModel()
    statusbar_vm = StatusBarViewModel()
    home_vm = HomeTabViewModel(app_state=state)
    settings_vm = SettingsTabViewModel(app_state=state, theme=theme)
    tab_vm = TabViewModel(app_state=state)
    tab_vm.register("home", "Home", glyph("home"))
    tab_vm.register("settings", "Settings", glyph("settings"))

    # Mutual exclusion: als één opent, sluit de andere
    menu_vm.menuOpenChanged.connect(
        lambda: statusbar_vm.closePluginDropdown() if menu_vm.menuOpen else None
    )
    statusbar_vm.pluginDropdownOpenChanged.connect(
        lambda: menu_vm.closeMenu() if statusbar_vm.pluginDropdownOpen else None
    )

    icons = Icons()

    engine = QQmlApplicationEngine()
    ctx = engine.rootContext()
    ctx.setContextProperty("appName", APP_NAME)
    ctx.setContextProperty("theme", theme)
    ctx.setContextProperty("icons", icons)
    ctx.setContextProperty("menuViewModel", menu_vm)
    ctx.setContextProperty("statusBarViewModel", statusbar_vm)
    ctx.setContextProperty("tabViewModel", tab_vm)
    ctx.setContextProperty("homeTabViewModel", home_vm)
    ctx.setContextProperty("settingsTabViewModel", settings_vm)

    qml_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "qml", "main.qml"
    )
    engine.load(QUrl.fromLocalFile(qml_path))

    if not engine.rootObjects():
        sys.exit(-1)

    # ── Platform-specifieke vensterbesturing ──────────────────────────────────
    window = engine.rootObjects()[0]
    dpr = app.devicePixelRatio()

    _wnd_proc = None  # Windows only: MOET bewaard blijven — anders GC → crash
    _win_ctrl = None

    if sys.platform == "win32":
        from tinyui_qml.windowing.win_window import (
            WindowController,
            apply_dwm_frame,
            install_wnd_proc,
        )

        hwnd = int(window.winId())
        # WndProc EERST installeren — apply_dwm_frame triggert WM_NCCALCSIZE
        _wnd_proc, _set_left = install_wnd_proc(
            hwnd,
            title_bar_height=round(theme.titleBarHeight * dpr),
            resize_border=round(8 * dpr),
            resize_corner=round(20 * dpr),
            left_button_width=round(300 * dpr),  # initiële waarde; QML werkt dit bij
            right_button_width=round(142 * dpr),
        )
        apply_dwm_frame(hwnd)
        _win_ctrl = WindowController(hwnd, dpr=dpr, set_left_button_width=_set_left)

    elif sys.platform.startswith("linux") or sys.platform == "darwin":
        from tinyui_qml.windowing.unix_window import WindowController

        _win_ctrl = WindowController(window)

    if _win_ctrl is not None:
        engine.rootContext().setContextProperty("windowController", _win_ctrl)

    # Engine opruimen vóór Python-objecten worden vrijgegeven
    app.aboutToQuit.connect(engine.deleteLater)

    exit_code = app.exec()

    # Expliciete opruiming in de juiste volgorde
    del engine
    del _win_ctrl
    del tab_vm
    del settings_vm
    del home_vm
    del menu_vm
    del statusbar_vm
    del icons
    del theme
    del state

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
