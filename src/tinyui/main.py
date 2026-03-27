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
from time import perf_counter
from typing import TYPE_CHECKING, Callable, cast

import PySide6
from PySide6.QtCore import QObject, QUrl, QtMsgType, qInstallMessageHandler, qVersion
from PySide6.QtQuick import QQuickWindow

from tinycore.app import App
from tinycore.inspect import LogInspector
from tinycore.logging import get_logger
from tinycore.plugin.lifecycle import PluginLifecycleManager
from tinycore.qt.app import create_application
from tinycore.qt.engine import create_engine
from tinyui.const import APP_NAME, VERSION
from tinyui.theme import Theme
from tinyui.viewmodels.core_viewmodel import CoreViewModel
from tinyui.viewmodels.menu_viewmodel import MenuViewModel
from tinyui.viewmodels.settings_panel_viewmodel import SettingsPanelViewModel
from tinyui.viewmodels.statusbar_viewmodel import StatusBarViewModel
from tinyui.viewmodels.tab_viewmodel import TabViewModel

if TYPE_CHECKING:
    from tinydevtools.host import DevToolsUiAttachment


def _qt_message_handler(mode, context, message):
    _qt_log = logging.getLogger("qt")
    if mode == QtMsgType.QtFatalMsg or mode == QtMsgType.QtCriticalMsg:
        _qt_log.error("Qt: %s", message)
    elif mode == QtMsgType.QtWarningMsg:
        _qt_log.warning("Qt: %s", message)
    else:
        _qt_log.debug("Qt: %s", message)


def _log_startup_phase(log, phase: str, start: float) -> None:
    log.startup_phase(phase, (perf_counter() - start) * 1000)


def _attach_devtools_ui(engine, log_inspector: LogInspector) -> "DevToolsUiAttachment | None":
    try:
        from tinydevtools.host import attach_ui
    except ImportError:
        return None

    frozen_root = getattr(sys, "_MEIPASS", None)
    return attach_ui(
        engine,
        log_inspector,
        frozen_root=frozen_root if isinstance(frozen_root, str) else None,
    )


def launch(core: App, lifecycle: PluginLifecycleManager,
           *, pre_run: Callable[[], None] | None = None,
           extra_context: dict[str, object] | None = None) -> int:
    """Initialize and run the tinyui main window.

    Called by the composition root after tinycore is fully booted.
    Returns the Qt exit code.
    """
    total_start = perf_counter()
    qInstallMessageHandler(_qt_message_handler)

    # ── Qt setup ──────────────────────────────────────────────────────────────
    phase_start = perf_counter()
    app = create_application(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(VERSION)
    log = get_logger(__name__)
    _log_startup_phase(log, "qt_app_setup", phase_start)

    log.info("── %s %s ──────────────────────────────", APP_NAME, VERSION)
    log.info("OS:      %s %s", platform.system(), platform.release())
    log.info("Python:  %s", platform.python_version())
    log.info("Qt:      %s  PySide6: %s", qVersion(), PySide6.__version__)
    log.info("Backend: %s", app.platformName())
    log.info("Editors: %d", len(core.host.editors.all()))

    # ── ViewModels ────────────────────────────────────────────────────────────
    phase_start = perf_counter()
    log_inspector   = LogInspector()
    theme        = Theme()
    menu_vm      = MenuViewModel()
    statusbar_vm = StatusBarViewModel()
    settings_vm  = SettingsPanelViewModel()
    core_vm      = CoreViewModel(core)
    tab_vm       = TabViewModel()

    tab_vm.register("widgets", "Widgets")
    _log_startup_phase(log, "viewmodels", phase_start)

    # ── Plugin switching — driven by the status bar ───────────────────────────
    _plugin_names = [p.name for p in core.runtime.plugins.plugins]

    def _on_plugin_switch() -> None:
        idx = cast(int, statusbar_vm.property("activePluginIndex"))
        if 0 <= idx < len(_plugin_names):
            lifecycle.activate(_plugin_names[idx])

    def _maybe_int(value: object) -> int | None:
        return int(value) if isinstance(value, int | float | str) else None

    statusbar_vm.activePluginIndexChanged.connect(_on_plugin_switch)

    # ── Settings — apply theme and persist on change ──────────────────────────
    def _apply_tinyui_settings() -> None:
        val = core.host.host_settings.get_value("TinyUI", "theme")
        if val:
            theme.load(val)

    def _save_setting(plugin_name: str) -> None:
        if core.host.host_settings.has_plugin(plugin_name):
            core.host.host_settings.save(plugin_name)
        else:
            core.host.plugin_settings.save(plugin_name)

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

    # ── QML engine ────────────────────────────────────────────────────────────
    phase_start = perf_counter()
    engine = create_engine()
    ctx = engine.rootContext()
    ctx.setContextProperty("appName",                APP_NAME)
    ctx.setContextProperty("theme",                  theme)
    ctx.setContextProperty("coreViewModel",          core_vm)
    ctx.setContextProperty("menuViewModel",          menu_vm)
    ctx.setContextProperty("statusBarViewModel",     statusbar_vm)
    ctx.setContextProperty("settingsPanelViewModel", settings_vm)
    ctx.setContextProperty("tabViewModel",           tab_vm)

    devtools_ui = _attach_devtools_ui(engine, log_inspector)
    ctx.setContextProperty("devToolsAvailable", devtools_ui is not None)
    ctx.setContextProperty("devToolsQmlPath", "" if devtools_ui is None else devtools_ui.qml_url)

    if extra_context:
        for key, value in extra_context.items():
            ctx.setContextProperty(key, value)

    frozen_root = getattr(sys, "_MEIPASS", None)
    if getattr(sys, "frozen", False) and isinstance(frozen_root, str):
        qml_dir = Path(frozen_root) / "tinyui" / "qml"
    else:
        qml_dir = Path(__file__).resolve().parent / "qml"
    engine.load(QUrl.fromLocalFile(str(qml_dir / "main.qml")))
    _log_startup_phase(log, "qml_load", phase_start)

    if not engine.rootObjects():
        core.stop()
        return -1

    # ── Platform windowing ────────────────────────────────────────────────────
    phase_start = perf_counter()
    window_obj = engine.rootObjects()[0]
    if not isinstance(window_obj, QQuickWindow):
        core.stop()
        return -1
    window = window_obj
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
            title_bar_height   = round(cast(float, theme.property("titleBarHeight")) * dpr),
            resize_border      = round(cast(float, theme.property("resizeBorder")) * dpr),
            resize_corner      = round(cast(float, theme.property("resizeCorner")) * dpr),
            left_button_width  = round(cast(float, theme.property("leftButtonWidth")) * dpr),
            right_button_width = round(cast(float, theme.property("rightButtonWidth")) * dpr),
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
    _log_startup_phase(log, "windowing", phase_start)

    # ── Window state restore ──────────────────────────────────────────────────
    if core.host.host_settings.get_value("TinyUI", "remember_position"):
        x = core.host.host_settings.get_value("TinyUI", "_position_x")
        y = core.host.host_settings.get_value("TinyUI", "_position_y")
        x_pos = _maybe_int(x)
        y_pos = _maybe_int(y)
        if x_pos is not None and y_pos is not None:
            window.setX(x_pos)
            window.setY(y_pos)

    if core.host.host_settings.get_value("TinyUI", "remember_size"):
        w = core.host.host_settings.get_value("TinyUI", "_window_width")
        h = core.host.host_settings.get_value("TinyUI", "_window_height")
        width = _maybe_int(w)
        height = _maybe_int(h)
        if width is not None and height is not None:
            window.setWidth(width)
            window.setHeight(height)

    # ── Run ───────────────────────────────────────────────────────────────────
    def _save_window_state() -> None:
        if core.host.host_settings.get_value("TinyUI", "remember_position"):
            core.host.host_settings.set_value("TinyUI", "_position_x", window.x())
            core.host.host_settings.set_value("TinyUI", "_position_y", window.y())
        if core.host.host_settings.get_value("TinyUI", "remember_size"):
            core.host.host_settings.set_value("TinyUI", "_window_width",  window.width())
            core.host.host_settings.set_value("TinyUI", "_window_height", window.height())
        core.host.host_settings.save("TinyUI")

    app.aboutToQuit.connect(_save_window_state)
    app.aboutToQuit.connect(log_inspector.shutdown)
    app.aboutToQuit.connect(engine.deleteLater)
    app.aboutToQuit.connect(lifecycle.shutdown)
    app.aboutToQuit.connect(core.stop)
    if devtools_ui is not None:
        app.aboutToQuit.connect(devtools_ui.log_view_model.shutdown)

    # Closing the main window must explicitly quit so aboutToQuit fires
    # even when other windows (widget overlay) are still open.
    window.closing.connect(lambda: app.quit())

    if pre_run is not None:
        phase_start = perf_counter()
        pre_run()
        _log_startup_phase(log, "pre_run_callback", phase_start)
    if devtools_ui is not None:
        devtools_ui.log_view_model.replay()
    log.startup_phase("launch_ready_for_exec", (perf_counter() - total_start) * 1000)

    exit_code = app.exec()

    del engine
    del _win_ctrl
    del tab_vm
    del settings_vm
    del core_vm
    del menu_vm
    del statusbar_vm
    del theme
    del devtools_ui

    return exit_code
