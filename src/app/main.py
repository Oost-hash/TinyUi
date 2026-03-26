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

import tinycore.log as _log_mod
_log_mod.configure()  # must run before any other import emits log records

from .bootstrap import bootstrap_runtime, discover_manifests
from tinyui import launch


def _config_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent / "config"
    return Path(__file__).resolve().parents[2] / "data" / "plugin-config"


def _plugins_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent / "plugins"
    return Path(__file__).resolve().parents[1] / "plugins"


def main() -> None:
    manifests = discover_manifests(_plugins_dir())
    runtime = bootstrap_runtime(_config_dir(), manifests)

    def _pre_run() -> None:
        runtime.overlay.start()
        runtime.state_monitor.start()

    exit_code = launch(runtime.core, runtime.lifecycle, pre_run=_pre_run, extra_context=runtime.extra_context)
    runtime.state_monitor.shutdown()
    runtime.overlay.stop()
    sys.exit(exit_code)


if __name__ == "__main__":
    mp.freeze_support()
    main()
