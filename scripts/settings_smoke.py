from __future__ import annotations

# pyright: reportGeneralTypeIssues=false, reportCallIssue=false

import argparse
import time
from pathlib import Path

from PySide6.QtCore import QtMsgType, qInstallMessageHandler
from PySide6.QtGui import QGuiApplication
from PySide6.QtQuick import QQuickWindow

from tinycore.logging import LogInspector, configure
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
from tinyqt.host import attach_window_content, create_window_host
from tinyqt.launch import _qt_message_handler
from tinyqt.manifests import TinyQtAppManifest, TinyQtShellManifest, validate_manifest
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


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Load SettingsDialog with the real TinyUI runtime and verify it opens."
    )
    parser.add_argument(
        "--open-timeout",
        type=float,
        default=5.0,
        help="Seconds to wait for the settings dialog to become visible.",
    )
    parser.add_argument(
        "--close-timeout",
        type=float,
        default=5.0,
        help="Seconds to wait for the settings dialog to close again.",
    )
    parser.add_argument(
        "--qml-file",
        help="Optional QML file to load instead of the default settings dialog window.",
    )
    parser.add_argument(
        "--content-qml-file",
        help="Optional Item-based content QML file to attach into the host window.",
    )
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

    _bind_tab_plugin_switching(runtime, tab_vm)
    _bind_statusbar_plugin_switching(runtime, statusbar_vm)
    _bind_theme_settings(runtime, core_vm, settings_vm, theme)

    if paths.source_root is None:
        print("Settings smoke failed: source_root is unavailable in this runtime mode")
        runtime.shutdown()
        return 1

    dialog_qml = Path(args.qml_file).resolve() if args.qml_file else paths.source_root / "tinyqt_app" / "TinyUiSettingsWindow.qml"
    dialog_content_qml = (
        Path(args.content_qml_file).resolve()
        if args.content_qml_file
        else paths.source_root / "tinyui" / "qml" / "SettingsDialogContent.qml"
    )
    print(f"Loading: {dialog_qml}")

    app_manifest = validate_manifest(
        TinyQtAppManifest(
            app_id="tinyui.settings_dialog",
            title="Settings",
            root_qml=dialog_qml,
            shell=TinyQtShellManifest(
                use_window_menu_bar=False,
                use_tab_bar=False,
                use_status_bar=False,
                lazy_panel_loading=False,
            ),
            panels=(),
        )
    )
    host = create_window_host(
        runtime,
        app=app,
        qml_path=dialog_qml,
        app_manifest=app_manifest,
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
        print("Settings smoke failed: dialog did not load through tinyqt host")
        runtime.shutdown()
        return 1

    if args.content_qml_file and not attach_window_content(host.engine, host.window, dialog_content_qml):
        print("Settings smoke failed: settings content did not attach through tinyqt host")
        runtime.shutdown()
        return 1

    root = host.window
    if not isinstance(root, QQuickWindow):
        print(f"Settings smoke failed: root object is {type(root).__name__}, expected QQuickWindow")
        runtime.shutdown()
        return 1

    root.show()
    opened = _pump_events(args.open_timeout, lambda: root.isVisible())
    if not opened:
        print("Settings smoke failed: dialog did not become visible")
        runtime.shutdown()
        return 1
    print("Settings dialog opened successfully")

    root.hide()
    closed = _pump_events(args.close_timeout, lambda: not root.isVisible())
    if not closed:
        print("Settings smoke failed: dialog did not close cleanly")
        runtime.shutdown()
        return 1
    print("Settings dialog closed successfully")

    runtime.shutdown()
    return 0
if __name__ == "__main__":
    raise SystemExit(main())
