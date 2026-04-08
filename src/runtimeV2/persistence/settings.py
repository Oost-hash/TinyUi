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

"""Settings store for runtime V2 persistence."""

from __future__ import annotations

import json
from typing import Any

from runtimeV2.persistence.contracts import PersistencePaths
from runtimeV2.persistence.schemas.settings import SettingDecl


class SettingsStore:
    """Store settings specs and values for one config set."""

    SETTINGS_FILE = "settings.json"

    def __init__(self, paths: PersistencePaths, active_set: str) -> None:
        self._paths = paths
        self._active_set = active_set
        self._specs: dict[str, list[SettingDecl]] = {}
        self._values: dict[str, dict[str, Any]] = {}

    def register_specs(self, specs_by_namespace: dict[str, list[SettingDecl]]) -> None:
        """Register plugin-provided setting specs."""

        for namespace, specs in specs_by_namespace.items():
            self._specs[namespace] = list(specs)
            values = self._values.setdefault(namespace, {})
            for spec in specs:
                values.setdefault(spec.key, spec.default)
        self.load()

    def specs_by_namespace(self) -> dict[str, list[SettingDecl]]:
        """Return registered settings specs."""

        return {namespace: list(specs) for namespace, specs in self._specs.items()}

    def get(self, namespace: str, key: str) -> Any:
        """Return one setting value."""

        return self._values.get(namespace, {}).get(key)

    def set(self, namespace: str, key: str, value: Any) -> None:
        """Set one setting value."""

        self._validate(namespace, key, value)
        self._values.setdefault(namespace, {})[key] = value

    def load(self) -> None:
        """Load persisted values for registered namespaces."""

        for namespace in self._specs:
            path = self._settings_path(namespace)
            if not path.exists():
                continue
            values = json.loads(path.read_text(encoding="utf-8"))
            self._values.setdefault(namespace, {}).update(values)

    def save(self, namespace: str) -> None:
        """Save one namespace."""

        path = self._settings_path(namespace)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(self._values.get(namespace, {}), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def save_all(self) -> None:
        """Save all registered namespaces."""

        for namespace in self._specs:
            self.save(namespace)

    def _settings_path(self, namespace: str):
        return self._paths.namespace_dir(self._active_set, namespace) / self.SETTINGS_FILE

    def _validate(self, namespace: str, key: str, value: Any) -> None:
        spec = next((item for item in self._specs.get(namespace, []) if item.key == key), None)
        if spec is None:
            return
        expected = {
            "bool": bool,
            "str": str,
            "int": int,
            "float": (int, float),
            "choice": str,
        }.get(spec.type)
        if expected is not None and not isinstance(value, expected):
            raise TypeError(f"Setting '{key}' expects {spec.type}")
        if spec.type == "choice" and value not in spec.choices:
            raise ValueError(f"Setting '{key}' value is not one of {spec.choices}")
