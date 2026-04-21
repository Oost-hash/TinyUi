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

from typing import Any

from runtimeV2.persistence.manifest.settings import SettingDecl
from runtimeV2.persistence.repository import PersistenceRepository


class SettingsStore:
    """Store settings specs and values."""

    def __init__(self, repository: PersistenceRepository) -> None:
        self._repository = repository
        self._specs: dict[str, list[SettingDecl]] = {}
        self._values: dict[str, dict[str, Any]] = {}

    def register_specs(self, specs_by_namespace: dict[str, list[SettingDecl]]) -> None:
        """Register manifest-provided setting specs."""

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

    def values_by_namespace(self) -> dict[str, dict[str, Any]]:
        """Return current values by namespace."""

        return {
            namespace: dict(values)
            for namespace, values in self._values.items()
        }

    def namespace_values(self, namespace: str) -> dict[str, Any]:
        """Return all values for one namespace."""

        return dict(self._values.get(namespace, {}))

    def set(self, namespace: str, key: str, value: Any) -> None:
        """Set one setting value."""

        self._validate(namespace, key, value)
        self._values.setdefault(namespace, {})[key] = value

    def load(self) -> None:
        """Load persisted values for registered namespaces."""

        for namespace in self._specs:
            document = self._repository.read_one("settings_values", {"namespace": namespace})
            if document is None:
                continue
            values = dict(document.get("values", {}))
            namespace_values = self._values.setdefault(namespace, {})
            for key, value in values.items():
                if not self._has_spec(namespace, key):
                    continue
                try:
                    self._validate(namespace, key, value)
                except (TypeError, ValueError):
                    continue
                namespace_values[key] = value

    def save(self, namespace: str) -> None:
        """Save one namespace."""

        self._repository.write_one(
            "settings_values",
            {"namespace": namespace},
            {"values": self._values.get(namespace, {})},
        )

    def save_all(self) -> None:
        """Save all registered namespaces."""

        for namespace in self._specs:
            self.save(namespace)

    def _has_spec(self, namespace: str, key: str) -> bool:
        return any(item.key == key for item in self._specs.get(namespace, []))

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
