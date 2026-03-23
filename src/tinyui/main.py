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
"""tinyui.launch — Qt main window host.

Receives a fully booted core and lifecycle from the composition root.
Responsible only for Qt setup, viewmodels, engine, and windowing.
"""

from __future__ import annotations

import logging
import platform
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Callable

import PySide6
from PySide6.QtCore import QUrl, QtMsgType, qInstallMessageHandler, qVersion

from tinycore.qt import create_application, create_engine
from tinyui import log as app_log
from tinyui.const import APP_NAME, VERSION
from tinyui.icons import Icons, load_font
from tinyui.theme import Theme
from tinyui.viewmodels.core_viewmodel import CoreViewModel
from tinyui.viewmodels.log_viewmodel import LogViewModel
from tinyui.viewmodels.menu_viewmodel import MenuViewModel
from tinyui.viewmodels.settings_panel_viewmodel import SettingsPanelViewModel
from tinyui.viewmodels.statusbar_viewmodel import StatusBarViewModel
from tinyui.viewmodels.tab_viewmodel import TabViewModel

if TYPE_CHECKING:
    from tinycore import App, PluginLifecycleManager


def _qt_message_handler(mode, context, message):
    _qt_log = logging.getLogger("qt")
    if mode == QtMsgType.QtFatalMsg or mode == QtMsgType.QtCriticalMsg:
        _qt_log.error("Qt: %s", message)
    elif mode == QtMsgType.QtWarningMsg:
        _qt_log.warning("Qt: %s", message)
    else:
        _qt_log.debug("Qt: %s", message)


def launch(core: App, lifecycle: PluginLifecycleManager,
           *, pre_run: Callable[[], None] | None = None,
           extra_context: dict | None = None) -> int:
    """Initialize and run the tinyui main window.

    Called by the composition root after tinycore is fully booted.
    Returns the Qt exit code.
    """
    app_log.configure()
    qInstallMessageHandler(_qt_message_handler)

    # ── Qt setup ──────────────────────────────────────────────────────────────
    app = create_application(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    load_font()
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(VERSION)

    log = logging.getLogger(__name__)
    log.info("── %s %s ──────────────────────────────", APP_NAME, VERSION)
    log.info("OS:      %s %s", platform.system(), platform.release())
    log.info("Python:  %s", platform.python_version())
    log.info("Qt:      %s  PySide6: %s", qVersion(), PySide6.__version__)
    log.info("Backend: %s", app.platformName())
    log.info("Editors: %d", len(core.editors.all()))

    # ── ViewModels ────────────────────────────────────────────────────────────
    log_vm       = LogViewModel()   # install early — captures all subsequent log output
    theme        = Theme()
    menu_vm      = MenuViewModel()
    statusbar_vm = StatusBarViewModel()
    settings_vm  = SettingsPanelViewModel()
    core_vm      = CoreViewModel(core)
    tab_vm       = TabViewModel()

    tab_vm.register("widgets", "Widgets")

    # ── Plugin switching — driven by the status bar ───────────────────────────
    _plugin_names = [p.name for p in core.plugins.plugins]

    def _on_plugin_switch() -> None:
        idx = statusbar_vm.activePluginIndex
        if 0 <= idx < len(_plugin_names):
            lifecycle.activate(_plugin_names[idx])

    statusbar_vm.activePluginIndexChanged.connect(_on_plugin_switch)

    # ── Settings — apply theme and persist on change ──────────────────────────
    def _apply_tinyui_settings() -> None:
        val = core.host_settings.get_value("TinyUI", "theme")
        if val:
            theme.load(val)

    def _save_setting(plugin_name: str) -> None:
        if core.host_settings.has_plugin(plugin_name):
            core.host_settings.save(plugin_name)
        else:
            core.settings.save(plugin_name)

    core_vm.settingsChanged.connect(_apply_tinyui_settings)
    core_vm.settingValueChanged.connect(_save_setting)
    settings_vm.settingChangeRequested.connect(core_vm.setSettingValue)
    _apply_tinyui_settings()

    # Mutual exclusion: opening one panel closes the others
    menu_vm.menuOpenChanged.connect(
        lambda: statusbar_vm.closePluginDropdown() if menu_vm.menuOpen else None
    )
    statusbar_vm.pluginDropdownOpenChanged.connect(
        lambda: menu_vm.closeMenu() if statusbar_vm.pluginDropdownOpen else None
    )
    menu_vm.menuOpenChanged.connect(
        lambda: settings_vm.closePanel() if menu_vm.menuOpen else None
    )
    settings_vm.openChanged.connect(
        lambda: menu_vm.closeMenu() if settings_vm.open else None
    )

    icons = Icons()

    # ── QML engine ────────────────────────────────────────────────────────────
    engine = create_engine()
    ctx = engine.rootContext()
    ctx.setContextProperty("appName",                APP_NAME)
    ctx.setContextProperty("theme",                  theme)
    ctx.setContextProperty("icons",                  icons)
    ctx.setContextProperty("coreViewModel",          core_vm)
    ctx.setContextProperty("menuViewModel",          menu_vm)
    ctx.setContextProperty("statusBarViewModel",     statusbar_vm)
    ctx.setContextProperty("settingsPanelViewModel", settings_vm)
    ctx.setContextProperty("tabViewModel",           tab_vm)
    ctx.setContextProperty("logViewModel",           log_vm)

    if extra_context:
        for key, value in extra_context.items():
            ctx.setContextProperty(key, value)

    if getattr(sys, "frozen", False):
        qml_dir = Path(sys._MEIPASS) / "tinyui" / "qml"
    else:
        qml_dir = Path(__file__).resolve().parent / "qml"
    engine.load(QUrl.fromLocalFile(str(qml_dir / "main.qml")))

    if not engine.rootObjects():
        core.stop()
        return -1

    # ── Platform windowing ────────────────────────────────────────────────────
    window = engine.rootObjects()[0]
    dpr = app.devicePixelRatio()

    _wnd_proc = None   # Windows only: MUST be kept alive — otherwise GC → crash
    _win_ctrl = None
    _chrome_helper = None

    if sys.platform == "win32":
        from tinyui.windowing.win_window import (
            WindowController,
            WindowChromeHelper,
            apply_dwm_frame,
            install_wnd_proc,
        )
        hwnd = int(window.winId())
        _wnd_proc, _set_left = install_wnd_proc(
            hwnd,
            title_bar_height   = round(theme.titleBarHeight   * dpr),
            resize_border      = round(theme.resizeBorder      * dpr),
            resize_corner      = round(theme.resizeCorner      * dpr),
            left_button_width  = round(theme.leftButtonWidth   * dpr),
            right_button_width = round(theme.rightButtonWidth  * dpr),
        )
        apply_dwm_frame(hwnd)
        _win_ctrl      = WindowController(hwnd, dpr=dpr, set_left_button_width=_set_left)
        _chrome_helper = WindowChromeHelper(dpr=dpr)
        engine.rootContext().setContextProperty("windowChromeHelper", _chrome_helper)

    elif sys.platform.startswith("linux") or sys.platform == "darwin":
        from tinyui.windowing.unix_window import WindowController
        _win_ctrl = WindowController(window)

    if _win_ctrl is not None:
        engine.rootContext().setContextProperty("windowController", _win_ctrl)

    # ── Window state restore ──────────────────────────────────────────────────
    if core.host_settings.get_value("TinyUI", "remember_position"):
        x = core.host_settings.get_value("TinyUI", "_position_x")
        y = core.host_settings.get_value("TinyUI", "_position_y")
        if x is not None and y is not None:
            window.setX(int(x))
            window.setY(int(y))

    if core.host_settings.get_value("TinyUI", "remember_size"):
        w = core.host_settings.get_value("TinyUI", "_window_width")
        h = core.host_settings.get_value("TinyUI", "_window_height")
        if w is not None and h is not None:
            window.setWidth(int(w))
            window.setHeight(int(h))

    # ── Run ───────────────────────────────────────────────────────────────────
    def _save_window_state() -> None:
        if core.host_settings.get_value("TinyUI", "remember_position"):
            core.host_settings.set_value("TinyUI", "_position_x", window.x())
            core.host_settings.set_value("TinyUI", "_position_y", window.y())
        if core.host_settings.get_value("TinyUI", "remember_size"):
            core.host_settings.set_value("TinyUI", "_window_width",  window.width())
            core.host_settings.set_value("TinyUI", "_window_height", window.height())
        core.host_settings.save("TinyUI")

    app.aboutToQuit.connect(_save_window_state)
    app.aboutToQuit.connect(log_vm.shutdown)
    app.aboutToQuit.connect(engine.deleteLater)
    app.aboutToQuit.connect(lifecycle.shutdown)
    app.aboutToQuit.connect(core.stop)

    # Closing the main window must explicitly quit so aboutToQuit fires
    # even when other windows (widget overlay) are still open.
    window.closing.connect(lambda: app.quit())

    if pre_run is not None:
        pre_run()

    exit_code = app.exec()

    del engine
    del _win_ctrl
    del tab_vm
    del settings_vm
    del core_vm
    del menu_vm
    del statusbar_vm
    del icons
    del theme

    return exit_code
