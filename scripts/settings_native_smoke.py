from __future__ import annotations

# pyright: reportGeneralTypeIssues=false, reportCallIssue=false

import argparse
import time

from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QWidget

from tinycore.logging import LogInspector, configure
from tinycore.paths import AppPaths
from tinycore.plugin.user_files import sync_user_files
from tinycore.runtime.boot import boot_runtime, discover_manifests
from tinyqt.app import create_configured_application
from tinyqt.apps import TINYUI_HOST_ASSEMBLY, get_first_party_manifest
from tinyqt.apps.tinyui import _build_registrations
from tinyqt.app_identity import APP_NAME, VERSION
from tinyqt.host import create_window_host
from tinyqt.launch import _qt_message_handler
from tinyqt.theme import Theme
from tinyui.ui_bindings import (
    bind_statusbar_plugin_switching,
    bind_tab_plugin_switching,
    bind_theme_settings,
)
from tinyui.viewmodels.core_viewmodel import CoreViewModel
from tinyui.viewmodels.settings_panel_viewmodel import SettingsPanelViewModel
from tinyui.viewmodels.statusbar_viewmodel import StatusBarViewModel
from tinyui.viewmodels.tab_viewmodel import TabViewModel
from PySide6.QtCore import qInstallMessageHandler


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


def _find_settings_widget() -> QWidget | None:
    app = QGuiApplication.instance()
    if app is None:
        return None
    widget_app = app  # QApplication subclass at runtime
    top_level_widgets = getattr(widget_app, "topLevelWidgets", None)
    if not callable(top_level_widgets):
        return None
    for widget in top_level_widgets():
        if isinstance(widget, QWidget) and widget.windowTitle() == "Settings":
            return widget
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Open TinyUI and verify the native settings window appears.")
    parser.add_argument("--open-timeout", type=float, default=5.0)
    parser.add_argument("--close-timeout", type=float, default=5.0)
    args = parser.parse_args()

    paths = AppPaths.detect()
    manifests = discover_manifests(paths.plugins_dir)
    sync_user_files(paths.app_root, manifests)
    runtime = boot_runtime(paths, manifests, host_assembly=TINYUI_HOST_ASSEMBLY)

    qInstallMessageHandler(_qt_message_handler)
    app = create_configured_application(
        app_name=APP_NAME,
        version=VERSION,
        quit_on_last_window_closed=False,
    )

    theme = Theme()
    log_inspector = LogInspector()
    statusbar_vm = StatusBarViewModel()
    settings_vm = SettingsPanelViewModel()
    core_vm = CoreViewModel(runtime)
    tab_vm = TabViewModel()

    for participant in runtime.runtime.plugin_runtime.registered_participants:
        label = participant.manifest.display_name or participant.name
        tab_vm.register(participant.name, label)

    bind_tab_plugin_switching(runtime, tab_vm)
    bind_statusbar_plugin_switching(runtime, statusbar_vm)
    bind_theme_settings(runtime, core_vm, settings_vm, theme)

    manifest = get_first_party_manifest(paths, "tinyui.main")
    if manifest.root_qml is None:
        print("Settings native smoke failed: tinyui.main manifest has no root_qml")
        runtime.shutdown()
        return 1

    host = create_window_host(
        runtime,
        app=app,
        qml_path=manifest.root_qml,
        app_manifest=manifest,
        theme=theme,
        log_inspector=log_inspector,
        build_registrations=lambda _devtools_ui: _build_registrations(
            theme=theme,
            core_vm=core_vm,
            statusbar_vm=statusbar_vm,
            settings_vm=settings_vm,
            tab_vm=tab_vm,
            devtools_ui=None,
        ),
        extra_context=None,
        module="TinyUI",
    )
    if host is None:
        print("Settings native smoke failed: main window did not load")
        runtime.shutdown()
        return 1

    host.window.show()
    ready = _pump_events(args.open_timeout, lambda: host.window.isVisible())
    if not ready:
        print("Settings native smoke failed: main window did not become visible")
        runtime.shutdown()
        return 1

    controller = host.window.property("settingsController")
    toggle = getattr(controller, "toggle", None)
    if not callable(toggle):
        print("Settings native smoke failed: settings controller is unavailable")
        runtime.shutdown()
        return 1

    toggle()
    opened = _pump_events(args.open_timeout, lambda: _find_settings_widget() is not None)
    if not opened:
        print("Settings native smoke failed: native settings window did not appear")
        runtime.shutdown()
        return 1
    print("Native settings window opened successfully")

    toggle()
    closed = _pump_events(args.close_timeout, lambda: _find_settings_widget() is None)
    if not closed:
        print("Settings native smoke failed: native settings window did not close cleanly")
        runtime.shutdown()
        return 1
    print("Native settings window closed successfully")

    runtime.shutdown()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
