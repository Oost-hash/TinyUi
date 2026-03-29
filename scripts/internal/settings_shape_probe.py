from __future__ import annotations

# pyright: reportGeneralTypeIssues=false, reportCallIssue=false

import argparse
import time
from pathlib import Path

from PySide6.QtCore import qInstallMessageHandler
from PySide6.QtGui import QGuiApplication
from PySide6.QtQuick import QQuickWindow

from tinyruntime_schema import LogInspector
from tinyqt_logging import configure
from tinycore.paths import AppPaths
from tinyplugins.user_files import sync_user_files
from tinyruntime.boot import boot_runtime, discover_manifests
from tinyqt.app import create_configured_application
from tinyqt.apps import TINYUI_HOST_ASSEMBLY
from tinyqt.apps.tinyui import (
    _bind_statusbar_plugin_switching,
    _bind_tab_plugin_switching,
    _bind_theme_settings,
    _build_registrations,
)
from tinyqt.app_identity import APP_NAME, VERSION
from tinyqt.host import create_window_host
from tinyqt.launch import _qt_message_handler
from tinyqt.manifests import TinyQtAppManifest, TinyQtShellManifest, validate_manifest
from tinyqt.theme import Theme
from tinyqt_main.viewmodels.core_viewmodel import CoreViewModel
from tinyqt_settings.viewmodels.settings_panel_viewmodel import SettingsPanelViewModel
from tinyqt_main.viewmodels.statusbar_viewmodel import StatusBarViewModel
from tinyqt_main.viewmodels.tab_viewmodel import TabViewModel


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
    parser = argparse.ArgumentParser(description="Run a host-backed settings window shape probe.")
    parser.add_argument("qml_file", help="Absolute or workspace-relative path to the QML file to probe.")
    parser.add_argument("--timeout", type=float, default=2.0)
    args = parser.parse_args()

    qml_path = Path(args.qml_file)
    if not qml_path.is_absolute():
        qml_path = (Path.cwd() / qml_path).resolve()

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

    manifest = validate_manifest(
        TinyQtAppManifest(
            app_id="tinyui.settings_shape_probe",
            title="Settings Shape Probe",
            root_qml=qml_path,
            shell=TinyQtShellManifest(
                use_window_menu_bar=False,
                use_tab_bar=False,
                use_status_bar=False,
                lazy_panel_loading=False,
            ),
            panels=(),
        )
    )

    print(f"Loading probe: {qml_path}")
    host = create_window_host(
        runtime,
        app=app,
        qml_path=qml_path,
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
        print("Probe failed: host did not load window")
        runtime.shutdown()
        return 1

    root = host.window
    if not isinstance(root, QQuickWindow):
        print(f"Probe failed: root object is {type(root).__name__}, expected QQuickWindow")
        runtime.shutdown()
        return 1

    settings_vm.openPanel()
    opened = _pump_events(args.timeout, lambda: root.isVisible() and settings_vm.open)
    if not opened:
        print("Probe failed: window did not become visible")
        runtime.shutdown()
        return 1

    print("Probe opened successfully")
    settings_vm.closePanel()
    _pump_events(args.timeout, lambda: (not root.isVisible()) and (not settings_vm.open))
    runtime.shutdown()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
