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
import multiprocessing as mp
import os
import platform
import sys
from pathlib import Path

# Logging before all other imports — configure() sets up basicConfig
from tinyui import log as app_log

app_log.configure()

import PySide6
from PySide6.QtCore import QUrl, qVersion
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuick import QQuickWindow
from PySide6.QtQuickControls2 import QQuickStyle

from tinycore import PluginLifecycleManager, PluginSpec, SubprocessPlugin, create_app
from tinyui.plugin import TinyUIPlugin
from tinyui.const import APP_NAME, VERSION
from tinyui.icons import Icons, load_font
from tinyui.theme import Theme
from tinyui.viewmodels.core_viewmodel import CoreViewModel
from tinyui.viewmodels.menu_viewmodel import MenuViewModel
from tinyui.viewmodels.settings_panel_viewmodel import SettingsPanelViewModel
from tinyui.viewmodels.statusbar_viewmodel import StatusBarViewModel
from tinyui.viewmodels.tab_viewmodel import TabViewModel
from tinyui.viewmodels.tyre_demo_viewmodel import TyreDemoViewModel


def _config_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent / "config"
    return Path(__file__).resolve().parents[2] / "data" / "plugin-config"


def main():
    # ── tinycore boot — FIRST, before Qt ────────────────────────────────────
    core = create_app(
        _config_dir(),
        SubprocessPlugin(PluginSpec("plugins.demo",  "DemoPlugin")),
        SubprocessPlugin(PluginSpec("plugins.demo2", "Demo2Plugin")),
    )
    TinyUIPlugin().register(core)           # host outside plugin system
    core.loaders.load_all(core.config)
    core.settings.load_persisted()          # load plugin settings
    core.host_settings.load_persisted()     # load host settings
    core.start(plugins=False)               # lifecycle manager controls plugin startup

    # ── Qt setup ──────────────────────────────────────────────────────────────
    QQuickWindow.setDefaultAlphaBuffer(True)  # before app — alpha channel
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
    log.info("Plugins: %d widget(s), %d editor(s)",
             len(core.widgets.all()), len(core.editors.all()))

    # ── ViewModels ────────────────────────────────────────────────────────────
    theme         = Theme()
    menu_vm       = MenuViewModel()
    statusbar_vm  = StatusBarViewModel()
    settings_vm   = SettingsPanelViewModel()
    core_vm       = CoreViewModel(core)
    tab_vm        = TabViewModel()
    tyre_demo_vm  = TyreDemoViewModel()

    # Tabs — order determines StackLayout index
    tab_vm.register("widgets", "Widgets")
    tab_vm.register("demo",    "Demo")

    # ── Plugin lifecycle — start on demand, stop after 30s grace period ──────
    _plugin_names = [p.name for p in core.plugins.plugins]
    lifecycle = PluginLifecycleManager(core.plugins, grace_seconds=30.0)

    def _on_plugin_switch() -> None:
        idx = statusbar_vm.activePluginIndex
        if 0 <= idx < len(_plugin_names):
            lifecycle.activate(_plugin_names[idx])

    statusbar_vm.activePluginIndexChanged.connect(_on_plugin_switch)

    if _plugin_names:
        lifecycle.activate(_plugin_names[0])   # start eerste plugin direct

    # Settings change — apply theme and persist
    def _apply_tinyui_settings():
        val = core.host_settings.get_value("TinyUI", "theme")
        if val:
            theme.load(val)

    core_vm.settingsChanged.connect(_apply_tinyui_settings)
    def _save_setting(plugin_name: str) -> None:
        if core.host_settings.has_plugin(plugin_name):
            core.host_settings.save(plugin_name)
        else:
            core.settings.save(plugin_name)
    core_vm.settingValueChanged.connect(_save_setting)
    settings_vm.settingChangeRequested.connect(core_vm.setSettingValue)
    _apply_tinyui_settings()                # apply persisted theme on startup

    # Mutual exclusion: opening one closes the other
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
    engine = QQmlApplicationEngine()
    ctx = engine.rootContext()
    ctx.setContextProperty("appName",            APP_NAME)
    ctx.setContextProperty("theme",              theme)
    ctx.setContextProperty("icons",              icons)
    ctx.setContextProperty("coreViewModel",      core_vm)
    ctx.setContextProperty("menuViewModel",      menu_vm)
    ctx.setContextProperty("statusBarViewModel", statusbar_vm)
    ctx.setContextProperty("settingsPanelViewModel", settings_vm)
    ctx.setContextProperty("tabViewModel",           tab_vm)
    ctx.setContextProperty("tyreDemoViewModel",      tyre_demo_vm)

    qml_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "qml", "main.qml")
    engine.load(QUrl.fromLocalFile(qml_path))

    if not engine.rootObjects():
        core.stop()
        sys.exit(-1)

    # ── Platform-specifieke vensterbesturing ──────────────────────────────────
    window = engine.rootObjects()[0]
    dpr = app.devicePixelRatio()

    _wnd_proc = None  # Windows only: MUST be kept alive — otherwise GC → crash
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
            title_bar_height   = round(theme.titleBarHeight * dpr),
            resize_border      = round(8  * dpr),
            resize_corner      = round(20 * dpr),
            left_button_width  = round(300 * dpr),
            right_button_width = round(142 * dpr),
        )
        apply_dwm_frame(hwnd)
        _win_ctrl = WindowController(hwnd, dpr=dpr, set_left_button_width=_set_left)
        _chrome_helper = WindowChromeHelper(dpr=dpr)
        engine.rootContext().setContextProperty("windowChromeHelper", _chrome_helper)

    elif sys.platform.startswith("linux") or sys.platform == "darwin":
        from tinyui.windowing.unix_window import WindowController
        _win_ctrl = WindowController(window)

    if _win_ctrl is not None:
        engine.rootContext().setContextProperty("windowController", _win_ctrl)

    # ── Window state restore ───────────────────────────────────────────────────
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
    app.aboutToQuit.connect(tyre_demo_vm.shutdown)
    app.aboutToQuit.connect(engine.deleteLater)
    app.aboutToQuit.connect(lifecycle.shutdown)
    app.aboutToQuit.connect(core.stop)

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

    sys.exit(exit_code)


if __name__ == "__main__":
    mp.freeze_support()   # required on Windows with frozen/spawn
    main()
