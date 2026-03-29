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

Receives a booted CoreRuntime from tinyui_boot.
Responsible only for Qt setup, viewmodels, signal wiring, engine, and windowing.
"""

# pyright: reportCallIssue=false, reportGeneralTypeIssues=false, reportAttributeAccessIssue=false, reportArgumentType=false

from __future__ import annotations

import logging
import platform
import sys
from pathlib import Path
from time import perf_counter
from typing import Callable, cast

import PySide6
from PySide6.QtCore import QtMsgType, QUrl, qInstallMessageHandler, qVersion
from PySide6.QtQuick import QQuickWindow

from tinycore.logging import LogInspector, get_logger
from tinyqt.app import create_application
from tinyqt.engine import create_engine
from tinyqt.host import (
    attach_optional_devtools_ui,
    restore_window_state,
    wire_app_shutdown,
    wire_devtools_monitor,
)
from tinyqt.registration import SingletonRegistration, register_singletons
from tinyqt.windowing.controller_api import WindowControllerApi
from tinycore.runtime.core_runtime import CoreRuntime
from tinyui.app_info import AppInfo
from tinyui.const import APP_NAME, VERSION
from tinyui.theme import Theme
from tinyui.ui_adapters import (
    bind_statusbar_plugin_switching,
    bind_tab_plugin_switching,
    bind_theme_settings,
)
from tinyui.viewmodels.core_viewmodel import CoreViewModel
from tinyui.viewmodels.menu_viewmodel import MenuViewModel
from tinyui.viewmodels.settings_panel_viewmodel import SettingsPanelViewModel
from tinyui.viewmodels.statusbar_viewmodel import StatusBarViewModel
from tinyui.viewmodels.tab_viewmodel import TabViewModel


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


def launch(
    core: CoreRuntime,
    *,
    pre_run: Callable[[], None] | None = None,
    extra_context: dict[str, tuple[type, str, object]] | None = None,
) -> int:
    """Initialize and run the tinyui main window.

    Called by tinyui_boot after boot_runtime completes.
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
    log_inspector = LogInspector()
    theme = Theme()
    menu_vm = MenuViewModel()
    statusbar_vm = StatusBarViewModel()
    settings_vm = SettingsPanelViewModel()
    core_vm = CoreViewModel(core)
    tab_vm = TabViewModel()

    for participant in core.runtime.plugin_runtime.registered_participants:
        label = participant.manifest.display_name or participant.name
        tab_vm.register(participant.name, label)
    _log_startup_phase(log, "viewmodels", phase_start)

    bind_tab_plugin_switching(core, tab_vm)
    bind_statusbar_plugin_switching(core, statusbar_vm)

    bind_theme_settings(core, core_vm, settings_vm, theme)

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
    register_singletons(
        [
            SingletonRegistration(Theme, "TinyUI", "Theme", theme),
            SingletonRegistration(
                CoreViewModel, "TinyUI", "CoreViewModel", core_vm
            ),
            SingletonRegistration(MenuViewModel, "TinyUI", "MenuViewModel", menu_vm),
            SingletonRegistration(
                StatusBarViewModel, "TinyUI", "StatusBarViewModel", statusbar_vm
            ),
            SingletonRegistration(
                SettingsPanelViewModel,
                "TinyUI",
                "SettingsPanelViewModel",
                settings_vm,
            ),
            SingletonRegistration(TabViewModel, "TinyUI", "TabViewModel", tab_vm),
        ]
    )

    devtools_ui = attach_optional_devtools_ui(core, engine, log_inspector)
    app_info = AppInfo(
        app_name=APP_NAME,
        devtools_available=devtools_ui is not None,
        devtools_path="" if devtools_ui is None else devtools_ui.qml_url,
    )
    register_singletons(
        [SingletonRegistration(AppInfo, "TinyUI", "AppInfo", app_info)]
    )

    if extra_context:
        register_singletons(
            [
                SingletonRegistration(cls, module, name, instance)
                for name, (cls, module, instance) in extra_context.items()
            ]
        )

    qml_dir = core.paths.qml_dir("tinyui")
    engine.load(QUrl.fromLocalFile(str(qml_dir / "main.qml")))
    _log_startup_phase(log, "qml_load", phase_start)

    if not engine.rootObjects():
        core.shutdown()
        return -1

    # ── Platform windowing ────────────────────────────────────────────────────
    phase_start = perf_counter()
    window_obj = engine.rootObjects()[0]
    if not isinstance(window_obj, QQuickWindow):
        core.shutdown()
        return -1
    window = window_obj
    wire_devtools_monitor(core, window)
    dpr = app.devicePixelRatio()

    _wnd_proc = None      # Windows only: MUST be kept alive — otherwise GC → crash
    _win_ctrl = None
    _chrome_helper = None
    if sys.platform == "win32":
        from tinyqt.windowing.win_window import (
            WindowChromeHelper,
            WindowController,
            apply_dwm_frame,
            install_wnd_proc,
        )

        hwnd = int(window.winId())
        _wnd_proc, _set_left = install_wnd_proc(
            hwnd,
            title_bar_height=round(cast(float, theme.property("titleBarHeight")) * dpr),
            resize_border=round(cast(float, theme.property("resizeBorder")) * dpr),
            resize_corner=round(cast(float, theme.property("resizeCorner")) * dpr),
            left_button_width=round(
                cast(float, theme.property("leftButtonWidth")) * dpr
            ),
            right_button_width=round(
                cast(float, theme.property("rightButtonWidth")) * dpr
            ),
        )
        apply_dwm_frame(hwnd)
        _win_ctrl = WindowController(hwnd, dpr=dpr, set_left_button_width=_set_left)
        _chrome_helper = WindowChromeHelper(dpr=dpr)
        register_singletons(
            [
                SingletonRegistration(
                    WindowChromeHelper,
                    "TinyUI",
                    "WindowChromeHelper",
                    _chrome_helper,
                )
            ]
        )

    elif sys.platform.startswith("linux") or sys.platform == "darwin":
        from tinyqt.windowing.unix_window import WindowController

        _win_ctrl = WindowController(window)

    if _win_ctrl is not None:
        register_singletons(
            [
                SingletonRegistration(
                    WindowControllerApi,
                    "TinyUI",
                    "WindowController",
                    _win_ctrl,
                )
            ]
        )
    _log_startup_phase(log, "windowing", phase_start)
    if core.units.get("ui.main") is not None:
        core.units.set_state("ui.main", "running")

    # ── Window state restore ──────────────────────────────────────────────────
    restore_window_state(core, window, scope="TinyUI")

    # ── Run ───────────────────────────────────────────────────────────────────
    wire_app_shutdown(
        app,
        core,
        window=window,
        scope="TinyUI",
        log_inspector=log_inspector,
        engine=engine,
        devtools_ui=devtools_ui,
    )

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
