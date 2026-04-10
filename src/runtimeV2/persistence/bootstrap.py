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

from runtimeV2.contracts import BootstrapConfig


def load_bootstrap(path: Path) -> BootstrapConfig:
    """Load persistence bootstrap data."""

    if not path.exists():
        return BootstrapConfig()

    with path.open("rb") as handle:
        data = tomllib.load(handle)

    raw_config_root = data.get("config_root")
    config_root = Path(raw_config_root) if isinstance(raw_config_root, str) and raw_config_root else None
    raw_active_set = data.get("active_set")
    active_set = raw_active_set if isinstance(raw_active_set, str) and raw_active_set else "default"
    return BootstrapConfig(config_root=config_root, active_set=active_set)


def save_bootstrap(path: Path, config: BootstrapConfig) -> None:
    """Save persistence bootstrap data."""

    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [f'active_set = "{config.active_set}"']
    if config.config_root is not None:
        config_root = str(config.config_root).replace("\\", "\\\\").replace('"', '\\"')
        lines.insert(0, f'config_root = "{config_root}"')
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
