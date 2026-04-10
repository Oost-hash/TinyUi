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

"""Path registration for the runtime V2 paths domain."""

from __future__ import annotations

from pathlib import Path

from runtimeV2.paths.contracts import RuntimePaths


def register_app_paths(runtime_paths: RuntimePaths) -> dict[str, Path]:
    """Return the app paths exposed by the paths domain."""

    named_paths: dict[str, Path] = {
        "app_root": runtime_paths.app_root,
        "host_dir": runtime_paths.host_dir,
        "plugins_dir": runtime_paths.plugins_dir,
    }
    if runtime_paths.source_root is not None:
        named_paths["source_root"] = runtime_paths.source_root
    if runtime_paths.frozen_root is not None:
        named_paths["frozen_root"] = runtime_paths.frozen_root
    return named_paths
