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

"""Bootstrap loading for runtime V2 persistence."""

from __future__ import annotations

import tomllib
from pathlib import Path

from runtimeV2.persistence.contracts import BootstrapConfig


def load_bootstrap(path: Path) -> BootstrapConfig:
    """Load persistence bootstrap data."""

    if not path.exists():
        return BootstrapConfig()
    with path.open("rb") as handle:
        data = tomllib.load(handle)
    raw_backend = data.get("backend")
    return BootstrapConfig(
        backend=raw_backend if isinstance(raw_backend, str) and raw_backend else "sqlite",
    )


def save_bootstrap(path: Path, config: BootstrapConfig) -> None:
    """Save persistence bootstrap data."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f'backend = "{_toml_string(config.backend)}"\n', encoding="utf-8")


def _toml_string(value: str) -> str:
    """Escape a value for a basic TOML string."""

    return value.replace("\\", "\\\\").replace('"', '\\"')
