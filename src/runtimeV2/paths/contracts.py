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

from runtime.app.paths import AppPaths


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

    @classmethod
    def from_app_paths(cls, app_paths: AppPaths) -> "RuntimePaths":
        """Build runtime V2 paths from the current AppPaths detector."""

        return cls(
            app_root=app_paths.app_root,
            config_dir=app_paths.config_dir,
            host_dir=app_paths.host_dir,
            plugins_dir=app_paths.plugins_dir,
            data_dir=app_paths.data_dir,
            source_root=app_paths.source_root,
            frozen_root=app_paths.frozen_root,
        )

    def qml_dir(self, package: str) -> Path:
        """Return the QML directory for a package."""

        if self.frozen_root is not None:
            return self.frozen_root / package / "qml"
        if self.source_root is None:
            raise RuntimeError(f"No source root available for package '{package}'")
        return self.source_root / package / "qml"
