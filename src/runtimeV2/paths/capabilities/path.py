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

"""Path capability for the runtime V2 paths domain."""

from __future__ import annotations

from pathlib import Path

from runtimeV2.paths.contracts import RuntimePaths
from runtimeV2.paths.qml_source import QmlSource


class PathCapability:
    """Read-only interface over paths-domain data."""

    def __init__(self, *, runtime_paths: RuntimePaths, named_paths: dict[str, Path]) -> None:
        self._runtime_paths = runtime_paths
        self._named_paths = named_paths

    def get(self, name: str) -> Path:
        """Return a registered path by name."""

        try:
            return self._named_paths[name]
        except KeyError as exc:
            raise KeyError(f"Path '{name}' is not registered") from exc

    def qml_dir(self, package: str) -> Path:
        """Return the QML directory for a package.
        
        Deprecated: Use qml_source() for core UI QML files.
        """
        return self._runtime_paths.qml_dir(package)

    def qml_source(self, name: str) -> QmlSource:
        """Return a QML source by registered name.
        
        Supports both filesystem (dev) and QRC (build) modes.
        """
        return self._runtime_paths.qml_source(name)
