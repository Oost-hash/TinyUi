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
"""Shared application path ownership for source and packaged runtime modes."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppPaths:
    """Resolved application roots for the current runtime mode."""

    app_root: Path
    config_dir: Path
    plugins_dir: Path
    source_root: Path | None = None
    frozen_root: Path | None = None

    @classmethod
    def detect(cls) -> "AppPaths":
        """Resolve shared app roots for source mode or frozen mode."""
        if getattr(sys, "frozen", False):
            app_root = Path(sys.executable).resolve().parent
            meipass = getattr(sys, "_MEIPASS", None)
            frozen_root = (
                Path(meipass).resolve()
                if isinstance(meipass, str)
                else app_root / "_runtime"
            )
            return cls(
                app_root=app_root,
                config_dir=app_root / "config",
                plugins_dir=app_root / "plugins",
                source_root=None,
                frozen_root=frozen_root,
            )

        source_root = Path(__file__).resolve().parents[1]
        repo_root = source_root.parent
        return cls(
            app_root=source_root,
            config_dir=repo_root / "data" / "plugin-config",
            plugins_dir=source_root / "plugins",
            source_root=source_root,
            frozen_root=None,
        )

    def qml_dir(self, package: str) -> Path:
        """Return the QML directory for one package in the current runtime mode."""
        if self.frozen_root is not None:
            return self.frozen_root / package / "qml"
        if self.source_root is None:
            raise RuntimeError(f"No source root available for package '{package}'")
        return self.source_root / package / "qml"
