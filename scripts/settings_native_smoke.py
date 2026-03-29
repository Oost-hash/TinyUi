from __future__ import annotations

# pyright: reportGeneralTypeIssues=false, reportCallIssue=false

import argparse
import time

from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QWidget

from tinycore.logging import configure
from tinycore.paths import AppPaths
from tinycore.plugin.user_files import sync_user_files
from tinycore.runtime.boot import boot_runtime, discover_manifests
from tinyqt.app import create_configured_application
from tinyqt.apps import TINYUI_HOST_ASSEMBLY
from tinyqt.apps.tinyui import (
    _bind_statusbar_plugin_switching,
    _bind_tab_plugin_switching,
    _bind_theme_settings,
    _build_registrations,
)
from tinyqt.app_identity import APP_NAME, VERSION
from tinyqt.host import create_settings_controller
from tinyqt.theme import Theme
from tinyui.viewmodels.core_viewmodel import CoreViewModel
from tinyui.viewmodels.settings_panel_viewmodel import SettingsPanelViewModel
from tinyui.viewmodels.statusbar_viewmodel import StatusBarViewModel
from tinyui.viewmodels.tab_viewmodel import TabViewModel
configure()


def _pump_events(timeout_seconds: float, predicate) -> bool:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        QGuiApplication.processEvents()
        if predicate():
            return True
        time.sleep(0.02)
    QGuiApplication.processEvents()
    return predicate()


def _controller_window(controller) -> QWidget | None:
    window = getattr(controller, "_window", None)
    if isinstance(window, QWidget):
        return window
    return None


def _controller_window_visible(controller) -> bool:
    window = _controller_window(controller)
    return bool(window is not None and window.isVisible())


def main() -> int:
    parser = argparse.ArgumentParser(description="Open TinyUI and verify the native settings window appears.")
    parser.add_argument("--open-timeout", type=float, default=5.0)
    parser.add_argument("--close-timeout", type=float, default=5.0)
    args = parser.parse_args()

    paths = AppPaths.detect()
    manifests = discover_manifests(paths.plugins_dir)
    sync_user_files(paths.app_root, manifests)
    runtime = boot_runtime(paths, manifests, host_assembly=TINYUI_HOST_ASSEMBLY)

    app = create_configured_application(
        app_name=APP_NAME,
        version=VERSION,
        quit_on_last_window_closed=False,
    )

    theme = Theme()
    statusbar_vm = StatusBarViewModel()
    settings_vm = SettingsPanelViewModel()
    core_vm = CoreViewModel(runtime)
    tab_vm = TabViewModel()

    for participant in runtime.runtime.plugin_runtime.registered_participants:
        label = participant.manifest.display_name or participant.name
        tab_vm.register(participant.name, label)

    _bind_tab_plugin_switching(runtime, tab_vm)
    _bind_statusbar_plugin_switching(runtime, statusbar_vm)
    _bind_theme_settings(runtime, core_vm, settings_vm, theme)

    controller = create_settings_controller(
        app=None,
        core=runtime,
        theme=theme,
        build_registrations=lambda _devtools_ui: _build_registrations(
            theme=theme,
            core_vm=core_vm,
            statusbar_vm=statusbar_vm,
            settings_vm=settings_vm,
            tab_vm=tab_vm,
            devtools_ui=None,
        ),
    )

    controller.toggle()
    opened = _pump_events(
        args.open_timeout,
        lambda: _controller_window_visible(controller),
    )
    if not opened:
        print("Settings native smoke failed: native settings window did not appear")
        runtime.shutdown()
        return 1
    print("Native settings window opened successfully")

    controller.toggle()
    closed = _pump_events(
        args.close_timeout,
        lambda: not _controller_window_visible(controller),
    )
    if not closed:
        print("Settings native smoke failed: native settings window did not close cleanly")
        runtime.shutdown()
        return 1
    print("Native settings window closed successfully")

    runtime.shutdown()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
