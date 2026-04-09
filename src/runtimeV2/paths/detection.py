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

"""Runtime V2 path detection."""

from __future__ import annotations

import sys
from pathlib import Path

from runtimeV2.paths.contracts import RuntimePaths


def detect_runtime_paths() -> RuntimePaths:
    """Detect runtime V2 app/resource paths."""

    if getattr(sys, "frozen", False):
        app_root = Path(sys.executable).resolve().parent
        meipass = getattr(sys, "_MEIPASS", None)
        frozen_root = Path(meipass).resolve() if isinstance(meipass, str) else app_root / "tinyui"
        runtime_paths = RuntimePaths(
            app_root=app_root,
            config_dir=app_root / "config",
            host_dir=frozen_root / "plugins" / "tinyui",
            plugins_dir=app_root / "plugins",
            data_dir=app_root / "data",
            source_root=None,
            frozen_root=frozen_root,
        )
    else:
        source_root = Path(__file__).resolve().parents[2]
        repo_root = source_root.parent
        runtime_paths = RuntimePaths(
            app_root=source_root,
            config_dir=repo_root / "data" / "config",
            host_dir=source_root / "plugins" / "tinyui",
            plugins_dir=source_root / "plugins",
            data_dir=repo_root / "data" / "state",
            source_root=source_root,
            frozen_root=None,
        )

    runtime_paths.config_dir.mkdir(parents=True, exist_ok=True)
    runtime_paths.data_dir.mkdir(parents=True, exist_ok=True)
    return runtime_paths
