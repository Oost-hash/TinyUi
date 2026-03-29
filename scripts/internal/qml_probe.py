"""Internal QML probe runner for TinyQt/TinyUI shell validation."""
# pyright: reportGeneralTypeIssues=false, reportArgumentType=false, reportCallIssue=false

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import Callable, cast

from PySide6.QtCore import QtMsgType, QTimer, qInstallMessageHandler, qVersion

import PySide6

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
INTERNAL_QML = ROOT / "scripts" / "internal" / "qml"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from tinyruntime_schema.log_records import LogInspector
from tinyruntime_schema.runtime_state import RuntimeInspector
from tinycore.paths import AppPaths
from tinyruntime.models import RuntimeUnitInfo
from tinyqt_devtools.viewmodels.log_settings_viewmodel import LogSettingsViewModel
from tinyqt_devtools.viewmodels.log_viewmodel import LogViewModel
from tinyqt_devtools.viewmodels.runtime_viewmodel import RuntimeViewModel
from tinyqt_devtools.viewmodels.state_monitor_viewmodel import StateMonitorViewModel
from tinyqt.app import create_configured_application
from tinyqt.app_info import AppInfo
from tinyqt.apps import get_first_party_manifest
from tinyqt.engine import create_engine
from tinyqt.manifests import TinyQtAppManifest, validate_manifest, validate_required_singletons
from tinyqt.registration import SingletonRegistration, register_singletons
from tinyqt.theme import Theme  # pyright: ignore[reportGeneralTypeIssues]
from tinyqt_main.viewmodels.tab_viewmodel import TabViewModel

ThemeClass = cast(type[Theme], Theme)
AppInfoClass = cast(type[AppInfo], AppInfo)
TabViewModelClass = cast(type[TabViewModel], TabViewModel)
StateMonitorViewModelClass = cast(type[StateMonitorViewModel], StateMonitorViewModel)
RuntimeViewModelClass = cast(type[RuntimeViewModel], RuntimeViewModel)
LogViewModelClass = cast(type[LogViewModel], LogViewModel)
LogSettingsViewModelClass = cast(type[LogSettingsViewModel], LogSettingsViewModel)


def _qt_message_handler(mode, context, message):
    prefix = {
        QtMsgType.QtDebugMsg: "DEBUG",
        QtMsgType.QtInfoMsg: "INFO",
        QtMsgType.QtWarningMsg: "WARNING",
        QtMsgType.QtCriticalMsg: "ERROR",
        QtMsgType.QtFatalMsg: "FATAL",
    }.get(mode, "QT")
    print(f"{prefix}: {message}")


class _ProbeRuntimeCore:
    def __init__(self) -> None:
        self._units = [
            RuntimeUnitInfo(
                id="host.main",
                kind="process",
                role="host.main",
                owner="tinycore.runtime",
                transport="host",
                state="running",
                pid=4242,
            ),
            RuntimeUnitInfo(
                id="ui.main",
                kind="adapter",
                role="ui.main",
                owner="tinyui",
                transport="host",
                state="running",
                parent_id="host.main",
                pid=4242,
                execution_policy="host",
                activation_policy="always",
            ),
            RuntimeUnitInfo(
                id="devtools.monitor",
                kind="timer",
                role="devtools.monitor",
                owner="tinyqt_devtools",
                transport="qt_timer",
                state="idle",
                parent_id="host.main",
                pid=4242,
                execution_policy="host",
                activation_policy="on_demand",
                schedule_kind="interval",
                schedule_clock="qt",
                schedule_driver="runtime.qt_timer",
                interval_ms=400,
            ),
        ]

    def unit_infos(self) -> list[RuntimeUnitInfo]:
        return list(self._units)

    def scheduled_task_ids(self) -> tuple[str, ...]:
        return ("runtime.refresh", "devtools.snapshot")


def _tinyui_shell_registrations() -> list[SingletonRegistration]:
    tab_vm = TabViewModelClass()
    tab_vm.register("probe-a", "Probe A")
    tab_vm.register("probe-b", "Probe B")
    return [
        SingletonRegistration(ThemeClass, "TinyUI", "Theme", ThemeClass()),
        SingletonRegistration(
            AppInfoClass,
            "TinyUI",
            "AppInfo",
            AppInfoClass(
                app_name="TinyUiQmlProbe",
                devtools_available=True,
                devtools_path="",
            ),
        ),
        SingletonRegistration(TabViewModelClass, "TinyUI", "TabViewModel", tab_vm),
    ]


def _tinyqt_devtools_shell_registrations() -> list[SingletonRegistration]:
    log_inspector = LogInspector()
    runtime_inspector = RuntimeInspector()
    runtime_inspector.add_snapshot_source(
        "probe.runtime",
        "Probe Runtime",
        "runtime",
        lambda: [
            ("session.state", "green"),
            ("session.track", "Spa"),
            ("car.speed", "132"),
            ("car.fuel", "41"),
        ],
    )
    runtime_inspector.add_snapshot_source(
        "probe.widgets",
        "Probe Widgets",
        "widget",
        lambda: [
            ("speed.label", "SPD"),
            ("speed.flash", "true"),
            ("fuel.label", "FUEL"),
        ],
    )
    runtime_core = _ProbeRuntimeCore()
    state_vm = StateMonitorViewModelClass(runtime_inspector)
    runtime_vm = RuntimeViewModelClass(runtime_core)  # pyright: ignore[reportArgumentType]
    log_vm = LogViewModelClass(log_inspector)
    log_settings_vm = LogSettingsViewModelClass()
    logging.getLogger("qml_probe").warning("Probe warning")
    return [
        SingletonRegistration(
            StateMonitorViewModelClass,
            "TinyDevTools",
            "StateMonitorViewModel",
            state_vm,
        ),
        SingletonRegistration(
            RuntimeViewModelClass,
            "TinyDevTools",
            "RuntimeViewModel",
            runtime_vm,
        ),
        SingletonRegistration(
            LogViewModelClass,
            "TinyDevTools",
            "LogViewModel",
            log_vm,
        ),
        SingletonRegistration(
            LogSettingsViewModelClass,
            "TinyDevTools",
            "LogSettingsViewModel",
            log_settings_vm,
        ),
    ]


def _probe_registration_map() -> dict[str, Callable[[], list[SingletonRegistration]]]:
    return {
        "AppInfo": _tinyui_shell_registrations,
        "Theme": _tinyui_shell_registrations,
        "TabViewModel": _tinyui_shell_registrations,
        "StateMonitorViewModel": _tinyqt_devtools_shell_registrations,
        "RuntimeViewModel": _tinyqt_devtools_shell_registrations,
        "LogViewModel": _tinyqt_devtools_shell_registrations,
        "LogSettingsViewModel": _tinyqt_devtools_shell_registrations,
    }


def _manifest_from_args(args) -> TinyQtAppManifest | None:
    paths = AppPaths.detect()
    manifest_id = args.app_manifest
    if manifest_id is None and args.tinyui_shell:
        manifest_id = "tinyui.main"
    if manifest_id is None and args.tinyqt_devtools_shell:
        manifest_id = "tinyqt_devtools.window"
    if manifest_id is None:
        return None
    return validate_manifest(get_first_party_manifest(paths, manifest_id))


def _required_probe_singletons(manifest: TinyQtAppManifest | None) -> list[SingletonRegistration]:
    if manifest is None:
        return []
    registration_builders = _probe_registration_map()
    required_names: list[str] = list(manifest.required_singletons)
    for panel in manifest.panels:
        required_names.extend(panel.required_singletons)
    if manifest.app_id == "tinyui.main":
        required_names.extend(("Theme", "AppInfo", "TabViewModel"))
    unique_names: list[str] = []
    seen: set[str] = set()
    for name in required_names:
        if name in seen:
            continue
        seen.add(name)
        unique_names.append(name)

    registrations: list[SingletonRegistration] = []
    registered_names: set[str] = set()
    for name in unique_names:
        builder = registration_builders.get(name)
        if builder is None:
            continue
        for registration in builder():
            if registration.name in registered_names:
                continue
            registered_names.add(registration.name)
            registrations.append(registration)

    missing = validate_required_singletons(manifest, registered_names)
    if missing:
        raise RuntimeError(
            "TinyQt probe manifest contract violation for "
            f"'{manifest.app_id}': missing required singletons: {', '.join(missing)}"
        )
    return registrations


def main() -> int:
    parser = argparse.ArgumentParser(description="Load an internal QML probe file.")
    parser.add_argument("qml_file", help="Path to the probe QML file.")
    parser.add_argument(
        "--linger-ms",
        type=int,
        default=250,
        help="Milliseconds to keep the probe app alive after successful load.",
    )
    parser.add_argument(
        "--tinyui-shell",
        action="store_true",
        help="Register the TinyUI shell singletons needed by Theme/AppInfo/TabViewModel probes.",
    )
    parser.add_argument(
        "--tinyqt_devtools-shell",
        action="store_true",
        help="Register TinyDevTools singleton stubs needed by DevToolsWindow probes.",
    )
    parser.add_argument(
        "--app-manifest",
        help="Resolve a first-party TinyQt app manifest id and register its required probe stubs.",
    )
    args = parser.parse_args()

    qml_path = Path(args.qml_file)
    if not qml_path.is_absolute():
        if qml_path.parts and qml_path.parts[0] == "src":
            legacy_path = (ROOT / qml_path).resolve()
            if legacy_path.exists():
                qml_path = legacy_path
            else:
                qml_path = (INTERNAL_QML / qml_path.name).resolve()
        else:
            qml_path = (INTERNAL_QML / qml_path).resolve()

    qInstallMessageHandler(_qt_message_handler)
    app = create_configured_application(
        app_name="TinyUiQmlProbe",
        version=PySide6.__version__,
        quit_on_last_window_closed=False,
    )
    engine = create_engine()

    manifest = _manifest_from_args(args)
    if manifest is not None:
        register_singletons(_required_probe_singletons(manifest))

    print(f"QML probe: {qml_path}")
    print(f"Qt: {qVersion()}  PySide6: {PySide6.__version__}")
    engine.load(qml_path.as_uri())

    if not engine.rootObjects():
        print("Probe failed: no root objects loaded")
        return 1

    print("Probe loaded successfully")
    QTimer.singleShot(max(args.linger_ms, 0), app.quit)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())

