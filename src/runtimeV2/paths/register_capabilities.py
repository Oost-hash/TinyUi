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

"""Capability registration for the runtime V2 paths domain."""

from __future__ import annotations

from pathlib import Path

from runtime.app.paths import AppPaths
from runtimeV2.paths.capabilities.path import PathCapability


def register_path_capabilities(
    *,
    app_paths: AppPaths,
    named_paths: dict[str, Path],
) -> PathCapability:
    """Create the capabilities exposed by the paths domain."""

    return PathCapability(app_paths=app_paths, named_paths=named_paths)
