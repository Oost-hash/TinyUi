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

"""ConfigSetManager — manages multiple configurations."""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from runtime.persistence.paths import ConfigResolver


@dataclass(frozen=True)
class ConfigSet:
    """A named configuration."""

    id: str  # "default", "race", "practice"
    name: str  # Display name
    description: str = ""
    created_at: str = ""  # ISO timestamp


class ConfigSetManager:
    """Manages multiple configurations (co-config).
    
    Users can switch between different configurations,
    for example "default", "race", "practice", etc.
    """

    DEFAULT_SET_ID = "default"
    SETS_FILE = "sets.json"

    def __init__(self, resolver: ConfigResolver) -> None:
        self._resolver = resolver
        self._sets: dict[str, ConfigSet] = {}
        self._active_id: str = self.DEFAULT_SET_ID
        self._load()

    def _sets_file(self) -> Path:
        """Path to sets.json."""
        return self._resolver.config_root / self.SETS_FILE

    def _load(self) -> None:
        """Load config sets from sets.json."""
        sets_path = self._sets_file()
        if sets_path.exists():
            try:
                data = json.loads(sets_path.read_text(encoding="utf-8"))
                self._active_id = data.get("active", self.DEFAULT_SET_ID)
                for item in data.get("sets", []):
                    cs = ConfigSet(**item)
                    self._sets[cs.id] = cs
            except Exception:
                # Corrupt file, start fresh
                pass

        # Ensure default set exists
        if self.DEFAULT_SET_ID not in self._sets:
            self._sets[self.DEFAULT_SET_ID] = ConfigSet(
                id=self.DEFAULT_SET_ID,
                name="Default",
                description="Default configuration",
                created_at=datetime.now().isoformat(),
            )
            self._save()

    def _save(self) -> None:
        """Save config sets to sets.json."""
        self._resolver.config_root.mkdir(parents=True, exist_ok=True)
        data: dict[str, Any] = {
            "active": self._active_id,
            "sets": [
                {
                    "id": cs.id,
                    "name": cs.name,
                    "description": cs.description,
                    "created_at": cs.created_at,
                }
                for cs in self._sets.values()
            ],
        }
        self._sets_file().write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    def list_sets(self) -> list[ConfigSet]:
        """All available config sets."""
        return list(self._sets.values())

    def get_active(self) -> ConfigSet:
        """Current active config set."""
        return self._sets.get(self._active_id, self._sets[self.DEFAULT_SET_ID])

    def get_active_id(self) -> str:
        """ID of current active config set."""
        return self._active_id

    def set_active(self, set_id: str) -> bool:
        """Switch to another config set.
        
        Note: this takes effect after application restart.
        """
        if set_id not in self._sets:
            return False
        self._active_id = set_id
        self._save()
        return True

    def create_set(self, set_id: str, name: str, description: str = "") -> ConfigSet | None:
        """Create a new config set."""
        if set_id in self._sets:
            return None
        if not set_id or "/" in set_id or "\\" in set_id:
            return None  # Invalid ID

        cs = ConfigSet(
            id=set_id,
            name=name,
            description=description,
            created_at=datetime.now().isoformat(),
        )
        self._sets[set_id] = cs

        # Create directory
        set_dir = self._resolver.config_set_dir(set_id)
        set_dir.mkdir(parents=True, exist_ok=True)

        self._save()
        return cs

    def delete_set(self, set_id: str) -> bool:
        """Delete a config set.
        
        Cannot delete the active set or the default set.
        """
        if set_id == self.DEFAULT_SET_ID:
            return False
        if set_id == self._active_id:
            return False
        if set_id not in self._sets:
            return False

        # Delete directory
        set_dir = self._resolver.config_set_dir(set_id)
        if set_dir.exists():
            shutil.rmtree(set_dir)

        del self._sets[set_id]
        self._save()
        return True

    def rename_set(self, set_id: str, new_name: str) -> bool:
        """Rename a config set."""
        if set_id not in self._sets:
            return False

        old_cs = self._sets[set_id]
        self._sets[set_id] = ConfigSet(
            id=old_cs.id,
            name=new_name,
            description=old_cs.description,
            created_at=old_cs.created_at,
        )
        self._save()
        return True
