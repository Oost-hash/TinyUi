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
from enum import StrEnum
from pathlib import Path
from typing import Any
from uuid import UUID


@dataclass(frozen=True)
class BootstrapConfig:
    """Bootstrap settings needed before the database can open."""

    backend: str = "sqlite"


@dataclass(frozen=True)
class PersistencePaths:
    """Resolved runtime persistence paths."""

    base_dir: Path
    cache_dir: Path
    logs_dir: Path
    bootstrap_path: Path
    app_database_path: Path
    overlays_dir: Path

    @property
    def database_path(self) -> Path:
        """Return the app database path for older callers."""

        return self.app_database_path

    def overlay_database_path(self, overlay_uuid: str) -> Path:
        """Return the SQLite database path for one overlay store."""

        normalized_uuid = str(UUID(overlay_uuid))
        return self.overlays_dir / normalized_uuid / "overlay.db"


class PersistenceStoreKind(StrEnum):
    """Physical persistence store kind."""

    APP = "app"
    OVERLAY = "overlay"


@dataclass(frozen=True)
class PersistenceStoreRef:
    """Reference to a physical persistence store."""

    kind: PersistenceStoreKind
    store_id: str = ""

    @classmethod
    def app(cls) -> "PersistenceStoreRef":
        """Return the app store reference."""

        return cls(PersistenceStoreKind.APP)

    @classmethod
    def overlay(cls, overlay_uuid: str) -> "PersistenceStoreRef":
        """Return an overlay store reference."""

        return cls(PersistenceStoreKind.OVERLAY, str(UUID(overlay_uuid)))


@dataclass(frozen=True)
class JsonPersistencePaths:
    """File-layout paths kept only for tests and migration."""

    config_root: Path

    def namespace_dir(self, namespace: str) -> Path:
        """Return a namespace directory in the legacy JSON layout."""

        return self.config_root / namespace


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
