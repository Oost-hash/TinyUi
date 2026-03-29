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
"""Shared bootstrap flow for hosted Qt applications."""

from __future__ import annotations

from time import perf_counter
from typing import Callable

from tinycore.logging import get_logger
from tinycore.paths import AppPaths
from tinycore.plugin.user_files import sync_user_files
from tinycore.runtime.boot import HostAssembly, boot_runtime, discover_manifests

from .launch import QtLaunchSpec, launch_qml_app

_log = get_logger(__name__)


def _log_startup_phase(phase: str, start: float, **extra: object) -> None:
    _log.startup_phase(phase, (perf_counter() - start) * 1000, **extra)


def boot_and_launch_qml_app(
    paths: AppPaths,
    *,
    host_assembly: HostAssembly,
    build_launch_spec: Callable[[object], QtLaunchSpec],
) -> int:
    """Boot the shared runtime and launch a hosted QML app."""
    total_start = perf_counter()
    plugins_dir = paths.plugins_dir

    phase_start = perf_counter()
    manifests = discover_manifests(plugins_dir)
    _log_startup_phase(
        "discover_manifests",
        phase_start,
        plugins=len(manifests),
        consumers=sum(1 for item in manifests if item.is_consumer),
        providers=sum(1 for item in manifests if item.is_provider),
    )

    phase_start = perf_counter()
    sync_result = sync_user_files(paths.app_root, manifests)
    _log_startup_phase(
        "sync_user_files",
        phase_start,
        installed=sync_result.installed,
        preserved=sync_result.preserved,
        left_unset=sync_result.left_unset,
        missing=sync_result.missing_sources,
    )

    phase_start = perf_counter()
    runtime = boot_runtime(paths, manifests, host_assembly=host_assembly)
    _log_startup_phase("bootstrap_runtime", phase_start)

    def _pre_run() -> None:
        pre_run_start = perf_counter()
        runtime.start_host_workers()
        _log_startup_phase("pre_run", pre_run_start)

    phase_start = perf_counter()
    spec = build_launch_spec(runtime)
    exit_code = launch_qml_app(
        runtime,
        spec,
        pre_run=_pre_run,
        extra_context=None,
    )
    _log_startup_phase("launch_returned", phase_start)
    _log_startup_phase("main_total_until_exit", total_start)
    return exit_code
