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

"""Path resolution for runtime V2 persistence."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from runtimeV2.contracts import AppIdentityReader
from runtimeV2.persistence.contracts import PersistencePaths


def resolve_persistence_paths(identity_read: AppIdentityReader) -> PersistencePaths:
    """Resolve persistence paths from host identity."""

    base_dir = _os_config_dir(identity_read.app_id())
    return PersistencePaths(
        base_dir=base_dir,
        cache_dir=base_dir / "cache",
        logs_dir=base_dir / "logs",
        bootstrap_path=base_dir / "bootstrap.toml",
        app_database_path=base_dir / "app.db",
        overlays_dir=base_dir / "overlays",
    )


def ensure_persistence_dirs(paths: PersistencePaths) -> None:
    """Create persistence base directories."""

    paths.base_dir.mkdir(parents=True, exist_ok=True)
    paths.cache_dir.mkdir(parents=True, exist_ok=True)
    paths.logs_dir.mkdir(parents=True, exist_ok=True)
    paths.overlays_dir.mkdir(parents=True, exist_ok=True)


def _os_config_dir(app_id: str) -> Path:
    """Return the OS-level user config directory for the app id."""

    if sys.platform == "win32":
        return Path(os.getenv("APPDATA", str(Path.home()))) / app_id
    return Path(os.getenv("XDG_CONFIG_HOME", str(Path.home() / ".config"))) / app_id
