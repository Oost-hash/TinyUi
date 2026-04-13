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

"""Contracts for the runtime V2 paths domain."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from runtimeV2.paths.qml_source import QmlSource


@dataclass(frozen=True)
class RuntimePaths:
    """Runtime V2 app/resource paths."""

    app_root: Path
    host_dir: Path
    plugins_dir: Path
    source_root: Path | None = None
    frozen_root: Path | None = None
    # QML sources that support both dev (filesystem) and build (QRC) modes
    qml_sources: dict[str, QmlSource] = field(default_factory=dict)

    def qml_dir(self, package: str) -> Path:
        """Return the QML directory for a package.
        
        Deprecated: Use qml_source() for core UI QML files.
        """
        if self.frozen_root is not None:
            return self.frozen_root / package / "qml"
        if self.source_root is None:
            raise RuntimeError(f"No source root available for package '{package}'")
        return self.source_root / package / "qml"

    def qml_source(self, name: str) -> QmlSource:
        """Return a QML source by registered name.
        
        Supports both filesystem (dev) and QRC (build) modes.
        Raises KeyError if not registered.
        """
        try:
            return self.qml_sources[name]
        except KeyError as exc:
            raise KeyError(f"QML source '{name}' is not registered") from exc
