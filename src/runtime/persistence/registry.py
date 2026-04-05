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

"""SettingsRegistry — central store for all user-configurable settings."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from runtime.persistence.paths import ConfigResolver
from runtime_schema import SettingsSpec


class SettingsRegistry:
    """Central store for settings. Now with config set support.
    
    Each config set has its own isolated settings. The registry manages
    settings for one specific config set.
    """

    SETTINGS_FILE = "settings.json"

    def __init__(
        self,
        resolver: ConfigResolver,
        config_set_id: str,
    ) -> None:
        self._resolver = resolver
        self._set_id = config_set_id
        self._specs: dict[str, list[SettingsSpec]] = {}
        self._values: dict[str, dict[str, Any]] = {}

    def _namespace_path(self, namespace: str) -> Path:
        """Directory for a namespace."""
        return self._resolver.namespace_dir(self._set_id, namespace)

    def _settings_path(self, namespace: str) -> Path:
        """Path to settings.json for a namespace."""
        return self._namespace_path(namespace) / self.SETTINGS_FILE

    # ── Registration ──────────────────────────────────────────────────────

    def register(self, namespace: str, spec: SettingsSpec) -> None:
        """Register a setting spec (called during boot)."""
        self._specs.setdefault(namespace, []).append(spec)
        self._values.setdefault(namespace, {}).setdefault(spec.key, spec.default)

    # ── Reading ───────────────────────────────────────────────────────────

    def get(self, namespace: str, key: str) -> Any:
        """Read current value."""
        return self._values.get(namespace, {}).get(key)

    def by_namespace(self) -> dict[str, list[SettingsSpec]]:
        """All specs per namespace."""
        return {ns: list(specs) for ns, specs in self._specs.items()}

    # ── Writing ───────────────────────────────────────────────────────────

    def set(self, namespace: str, key: str, value: Any) -> None:
        """Change value (not persisted until save)."""
        spec = next((s for s in self._specs.get(namespace, []) if s.key == key), None)
        if spec is not None:
            _validate(spec, value)
        self._values.setdefault(namespace, {})[key] = value

    # ── Persistence ───────────────────────────────────────────────────────

    def load_persisted(self) -> None:
        """Load saved values for all registered namespaces."""
        for namespace in self._specs:
            path = self._settings_path(namespace)
            if not path.exists():
                continue
            try:
                values = json.loads(path.read_text(encoding="utf-8"))
                self._values.setdefault(namespace, {}).update(values)
            except Exception:
                pass  # Corrupt file, keep defaults

    def save(self, namespace: str) -> None:
        """Save values for a namespace."""
        path = self._settings_path(namespace)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(self._values.get(namespace, {}), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def save_all(self) -> None:
        """Save all namespaces."""
        for namespace in self._specs:
            self.save(namespace)

    # ── Scoped access ─────────────────────────────────────────────────────

    def scoped(self, namespace: str) -> "ScopedSettings":
        """Get a scoped view for a single namespace."""
        return ScopedSettings(self, namespace)


class ScopedSettings:
    """View on a single namespace."""

    def __init__(self, registry: SettingsRegistry, namespace: str) -> None:
        self._registry = registry
        self._namespace = namespace

    def register(self, spec: SettingsSpec) -> None:
        """Register a spec in this namespace."""
        self._registry.register(self._namespace, spec)

    def get(self, key: str) -> Any:
        """Get a value."""
        return self._registry.get(self._namespace, key)

    def set(self, key: str, value: Any) -> None:
        """Set a value."""
        self._registry.set(self._namespace, key, value)

    def save(self) -> None:
        """Save this namespace."""
        self._registry.save(self._namespace)


def _validate(spec: SettingsSpec, value: Any) -> None:
    """Validate value against spec."""
    expected = {
        "bool": bool,
        "str": str,
        "int": int,
        "float": (int, float),
        "choice": str,
    }.get(spec.type)
    if expected and not isinstance(value, expected):
        raise TypeError(f"Setting '{spec.key}' expects {spec.type}")
    if spec.type == "choice" and value not in spec.choices:
        raise ValueError(f"Setting '{spec.key}': '{value}' not in {spec.choices}")
