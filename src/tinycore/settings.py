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
"""SettingsSpec + SettingsRegistry — declarative plugin settings."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class SettingsSpec:
    """Declares one setting that a plugin exposes."""

    key:         str
    label:       str
    type:        str        # "bool" | "enum" | "int" | "str"
    default:     Any
    description: str        = ""
    options:     list[str]  = field(default_factory=list)  # for enum type


class SettingsRegistry:
    """Stores SettingsSpecs registered by plugins and their current values."""

    def __init__(self) -> None:
        self._specs:  list[tuple[str, SettingsSpec]] = []   # (plugin_name, spec)
        self._values: dict[str, dict[str, Any]]      = {}   # {plugin: {key: val}}

    # ── Registration ──────────────────────────────────────────────────────

    def register(self, plugin_name: str, spec: SettingsSpec) -> None:
        """Register a setting spec for a plugin."""
        self._specs.append((plugin_name, spec))
        plugin_values = self._values.setdefault(plugin_name, {})
        plugin_values.setdefault(spec.key, spec.default)

    # ── Reading ───────────────────────────────────────────────────────────

    def all(self) -> list[tuple[str, SettingsSpec]]:
        """All (plugin_name, spec) pairs in registration order."""
        return list(self._specs)

    def by_plugin(self) -> dict[str, list[SettingsSpec]]:
        """Specs grouped by plugin name, preserving registration order."""
        result: dict[str, list[SettingsSpec]] = {}
        for plugin_name, spec in self._specs:
            result.setdefault(plugin_name, []).append(spec)
        return result

    def get_value(self, plugin_name: str, key: str) -> Any:
        return self._values.get(plugin_name, {}).get(key)

    # ── Writing ───────────────────────────────────────────────────────────

    def set_value(self, plugin_name: str, key: str, value: Any) -> None:
        self._values.setdefault(plugin_name, {})[key] = value

    def load_values(self, plugin_name: str, values: dict[str, Any]) -> None:
        """Bulk-load persisted values (e.g. from JSON on startup)."""
        self._values.setdefault(plugin_name, {}).update(values)

    def dump_values(self, plugin_name: str) -> dict[str, Any]:
        """Return current values for a plugin (e.g. for JSON persistence)."""
        return dict(self._values.get(plugin_name, {}))
