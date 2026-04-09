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

"""Config set catalog for runtime V2 persistence."""

from __future__ import annotations

import json
import shutil
from dataclasses import asdict

from runtimeV2.persistence.bootstrap import BootstrapConfig, load_bootstrap, save_bootstrap
from runtimeV2.persistence.contracts import ConfigSet, PersistencePaths


class ConfigSetCatalog:
    """Catalog of available config sets."""

    def __init__(self, paths: PersistencePaths) -> None:
        self._paths = paths
        self._sets: dict[str, ConfigSet] = {}
        self._active_set = load_bootstrap(paths.bootstrap_path).active_set
        self._load()

    def _load(self) -> None:
        if self._paths.config_sets_path.exists():
            data = json.loads(self._paths.config_sets_path.read_text(encoding="utf-8"))
            for item in data.get("sets", []):
                config_set = ConfigSet(
                    id=str(item["id"]),
                    name=str(item.get("name", item["id"])),
                    description=str(item.get("description", "")),
                    created_at=str(item.get("created_at", "")),
                )
                self._sets[config_set.id] = config_set

        if "default" not in self._sets:
            self._sets["default"] = ConfigSet(
                id="default",
                name="Default",
                description="Default configuration",
            )
            self.save()

        if self._active_set not in self._sets:
            self._active_set = "default"
            self._save_bootstrap()

    def save(self) -> None:
        """Save the catalog."""

        self._paths.config_sets_path.parent.mkdir(parents=True, exist_ok=True)
        self._paths.config_sets_path.write_text(
            json.dumps(
                {"sets": [asdict(config_set) for config_set in self._sets.values()]},
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

    def _save_bootstrap(self) -> None:
        """Persist the active config set selection."""

        bootstrap = BootstrapConfig(
            config_root=self._paths.config_root,
            active_set=self._active_set,
        )
        save_bootstrap(self._paths.bootstrap_path, bootstrap)

    def list_sets(self) -> list[ConfigSet]:
        """Return all config sets."""

        return list(self._sets.values())

    def active_set(self) -> ConfigSet:
        """Return the active config set."""

        return self._sets[self._active_set]

    def active_set_id(self) -> str:
        """Return the active config set id."""

        return self._active_set

    def create_set(self, set_id: str, name: str, description: str = "") -> ConfigSet:
        """Create one config set."""

        if set_id in self._sets:
            raise ValueError(f"Config set already exists: {set_id}")
        if not set_id or "/" in set_id or "\\" in set_id:
            raise ValueError(f"Invalid config set id: {set_id}")
        config_set = ConfigSet(id=set_id, name=name, description=description)
        self._sets[set_id] = config_set
        self._paths.config_set_dir(set_id).mkdir(parents=True, exist_ok=True)
        self.save()
        return config_set

    def set_active(self, set_id: str) -> bool:
        """Set the active config set."""

        if set_id not in self._sets:
            return False
        if self._active_set == set_id:
            return True
        self._active_set = set_id
        self._save_bootstrap()
        return True

    def delete_set(self, set_id: str) -> bool:
        """Delete one config set."""

        if set_id == "default" or set_id == self._active_set:
            return False
        if set_id not in self._sets:
            return False
        config_dir = self._paths.config_set_dir(set_id)
        if config_dir.exists():
            shutil.rmtree(config_dir)
        del self._sets[set_id]
        self.save()
        return True

    def rename_set(self, set_id: str, new_name: str) -> bool:
        """Rename one config set."""

        config_set = self._sets.get(set_id)
        if config_set is None:
            return False
        self._sets[set_id] = ConfigSet(
            id=config_set.id,
            name=new_name,
            description=config_set.description,
            created_at=config_set.created_at,
        )
        self.save()
        return True
