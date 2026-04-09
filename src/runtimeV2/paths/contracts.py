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

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RuntimePaths:
    """Runtime V2 app/resource paths."""

    app_root: Path
    config_dir: Path
    host_dir: Path
    plugins_dir: Path
    data_dir: Path
    source_root: Path | None = None
    frozen_root: Path | None = None

    def qml_dir(self, package: str) -> Path:
        """Return the QML directory for a package."""

        if self.frozen_root is not None:
            return self.frozen_root / package / "qml"
        if self.source_root is None:
            raise RuntimeError(f"No source root available for package '{package}'")
        return self.source_root / package / "qml"
