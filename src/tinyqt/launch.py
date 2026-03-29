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
"""Shared Qt runtime launch flow for TinyQt-hosted applications."""

from __future__ import annotations

import logging
import platform
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter
from typing import TYPE_CHECKING, Any, Callable, cast

import PySide6
from PySide6.QtCore import QtMsgType, qInstallMessageHandler, qVersion

from tinycore.logging import get_logger
from .devtools_support import DevToolsUiAttachment

from .app import create_configured_application
from .host import create_window_host, restore_window_state, wire_app_shutdown
from .manifests import TinyQtAppManifest, validate_manifest
from .registration import RegistrationMap, SingletonRegistration

if TYPE_CHECKING:
    from tinyqt.host import QtWindowHost


@dataclass(frozen=True)
class QtLaunchSpec:
    app_name: str
    version: str
    qml_path: Path
    app_manifest: TinyQtAppManifest
    theme: object
    log_inspector: object
    build_registrations: Callable[[DevToolsUiAttachment | None], list[SingletonRegistration]]
    restore_state_scope: str
    module: str = "TinyUI"
    on_host_ready: Callable[[QtWindowHost], None] | None = None
    on_before_exec: Callable[[QtWindowHost], None] | None = None


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


def launch_hosted_app(
    core,
    spec: QtLaunchSpec,
    *,
    pre_run: Callable[[], None] | None = None,
    extra_context: RegistrationMap | None = None,
) -> int:
    """Launch one hosted application through the shared TinyQt runtime host."""
    total_start = perf_counter()
    app_manifest = validate_manifest(spec.app_manifest)
    qInstallMessageHandler(_qt_message_handler)

    phase_start = perf_counter()
    app = create_configured_application(
        app_name=spec.app_name,
        version=spec.version,
        quit_on_last_window_closed=False,
    )
    log = get_logger(__name__)
    _log_startup_phase(log, "qt_app_setup", phase_start)

    log.info("── %s %s ──────────────────────────────", app_manifest.title, spec.version)
    log.info("OS:      %s %s", platform.system(), platform.release())
    log.info("Python:  %s", platform.python_version())
    log.info("Qt:      %s  PySide6: %s", qVersion(), PySide6.__version__)
    log.info("Backend: %s", app.platformName())
    log.info("Editors: %d", len(core.host.editors.all()))

    phase_start = perf_counter()
    host = create_window_host(
        core,
        app=app,
        qml_path=spec.qml_path,
        app_manifest=app_manifest,
        theme=spec.theme,
        log_inspector=spec.log_inspector,
        build_registrations=spec.build_registrations,
        extra_context=extra_context,
        module=spec.module,
    )
    _log_startup_phase(log, "qml_load", phase_start)
    if host is None:
        core.shutdown()
        return -1

    if spec.on_host_ready is not None:
        spec.on_host_ready(host)

    phase_start = perf_counter()
    if spec.on_before_exec is not None:
        spec.on_before_exec(host)
    _log_startup_phase(log, "windowing", phase_start)

    restore_window_state(core, host.window, scope=spec.restore_state_scope)
    wire_app_shutdown(
        app,
        core,
        window=host.window,
        scope=spec.restore_state_scope,
        log_inspector=spec.log_inspector,
        engine=host.engine,
        devtools_ui=host.devtools_ui,
    )
    host.window.closing.connect(lambda: app.quit())

    if pre_run is not None:
        phase_start = perf_counter()
        pre_run()
        _log_startup_phase(log, "pre_run_callback", phase_start)
    if host.devtools_ui is not None:
        replay = cast(Any, host.devtools_ui.log_view_model).replay
        if callable(replay):
            replay()
    log.startup_phase("launch_ready_for_exec", (perf_counter() - total_start) * 1000)

    exit_code = app.exec()

    del host
    return exit_code


def launch_qml_app(
    core,
    spec: QtLaunchSpec,
    *,
    pre_run: Callable[[], None] | None = None,
    extra_context: RegistrationMap | None = None,
) -> int:
    """Compatibility alias for the older QML-specific launch name."""
    return launch_hosted_app(
        core,
        spec,
        pre_run=pre_run,
        extra_context=extra_context,
    )
