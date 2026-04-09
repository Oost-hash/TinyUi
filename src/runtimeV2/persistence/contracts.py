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

"""Contracts for runtime V2 persistence."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class BootstrapConfig:
    """Bootstrap settings needed before persistence can load catalog data."""

    config_root: Path | None = None
    active_set: str = "default"


@dataclass(frozen=True)
class PersistencePaths:
    """Resolved persistence paths."""

    base_dir: Path
    config_root: Path
    cache_dir: Path
    logs_dir: Path
    bootstrap_path: Path
    config_sets_path: Path

    def config_set_dir(self, set_id: str) -> Path:
        """Return the directory for one config set."""

        return self.config_root / set_id

    def namespace_dir(self, set_id: str, namespace: str) -> Path:
        """Return the directory for a namespace inside a config set."""

        return self.config_set_dir(set_id) / namespace


@dataclass(frozen=True)
class ConfigSet:
    """One config set catalog record."""

    id: str
    name: str
    description: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class WidgetInstanceConfig:
    """Configuration of one widget instance."""

    widget_id: str
    enabled: bool = True
    position: tuple[int, int] = (0, 0)
    values: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON data."""

        return {
            "widget_id": self.widget_id,
            "enabled": self.enabled,
            "position": [self.position[0], self.position[1]],
            "values": self.values,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "WidgetInstanceConfig":
        """Build from JSON data."""

        raw_position = data.get("position", [0, 0])
        return cls(
            widget_id=str(data["widget_id"]),
            enabled=bool(data.get("enabled", True)),
            position=(
                int(raw_position[0]),
                int(raw_position[1]),
            ) if len(raw_position) >= 2 else (0, 0),
            values=dict(data.get("values", {})),
        )
