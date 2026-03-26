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
"""Composition root — the only place that knows about all layers.

Boot order:
  1. Scan plugin manifests
  2. Build tinycore with discovered plugins
  3. Register host settings
  4. Load persisted config/settings from disk
  5. Start core
  6. Activate plugins, register host-side connectors
  7. Build widget overlay from manifest widget declarations
  8. Hand off to tinyui for the Qt event loop
"""

from __future__ import annotations

import multiprocessing as mp
import sys
from pathlib import Path
from time import perf_counter

import tinycore.log as _log_mod
_log_mod.configure()  # must run before any other import emits log records

from .bootstrap import bootstrap_runtime, discover_manifests
from tinycore.plugin.user_files import sync_user_files
from tinyui.main import launch
from tinycore.log import get_logger

_log = get_logger(__name__)


def _log_startup_phase(phase: str, start: float, **extra: object) -> None:
    fields = " ".join(f"{key}={value}" for key, value in extra.items())
    suffix = f" {fields}" if fields else ""
    _log.info("startup phase=%s ms=%.1f%s", phase, (perf_counter() - start) * 1000, suffix)


def _config_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent / "config"
    return Path(__file__).resolve().parents[2] / "data" / "plugin-config"


def _plugins_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent / "plugins"
    return Path(__file__).resolve().parents[1] / "plugins"


def main() -> None:
    total_start = perf_counter()
    plugins_dir = _plugins_dir()

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
    sync_result = sync_user_files(plugins_dir.parent, manifests)
    _log_startup_phase(
        "sync_user_files",
        phase_start,
        installed=sync_result.installed,
        preserved=sync_result.preserved,
        left_unset=sync_result.left_unset,
        missing=sync_result.missing_sources,
    )

    phase_start = perf_counter()
    runtime = bootstrap_runtime(_config_dir(), manifests)
    _log_startup_phase("bootstrap_runtime", phase_start)

    def _pre_run() -> None:
        pre_run_start = perf_counter()
        runtime.overlay.start()
        runtime.state_monitor.start()
        _log_startup_phase("pre_run", pre_run_start)

    phase_start = perf_counter()
    exit_code = launch(runtime.core, runtime.lifecycle, pre_run=_pre_run, extra_context=runtime.extra_context)
    _log_startup_phase("launch_returned", phase_start)
    _log_startup_phase("main_total_until_exit", total_start)
    runtime.state_monitor.shutdown()
    runtime.overlay.stop()
    sys.exit(exit_code)


if __name__ == "__main__":
    mp.freeze_support()
    main()
