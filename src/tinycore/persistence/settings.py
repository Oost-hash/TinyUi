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
"""SettingsRegistry — plugin and host setting persistence."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from tinycore.logging import get_logger
from tinyqt_settings_schema import SettingsSpec

log = get_logger(__name__)


class SettingsRegistry:
    """Stores SettingsSpecs registered by plugins, their current values, and JSON persistence."""

    def __init__(self, config_dir: Path | None = None) -> None:
        self._dir:    Path | None                    = config_dir
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

    def has_plugin(self, name: str) -> bool:
        """Return True if any settings are registered under this plugin name."""
        return any(pn == name for pn, _ in self._specs)

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

    # ── Persistence ───────────────────────────────────────────────────────

    def _json_path(self, plugin_name: str) -> Path | None:
        return self._dir / plugin_name / "settings.json" if self._dir else None

    def load_persisted(self) -> None:
        """Load persisted JSON values for all registered plugins.

        Overrides spec defaults with saved values.
        Unknown keys (removed settings) are ignored.
        Call after register_all(), before start().
        """
        if not self._dir:
            return
        seen: set[str] = set()
        for plugin_name, _ in self._specs:
            if plugin_name in seen:
                continue
            seen.add(plugin_name)
            path = self._json_path(plugin_name)
            if path is None or not path.exists():
                continue
            try:
                with path.open(encoding="utf-8") as f:
                    values: dict = json.load(f)
                self.load_values(plugin_name, values)
                log.settings("loaded", plugin=plugin_name, values=len(values))
            except Exception as exc:
                log.warning("Could not load settings for %r: %s", plugin_name, exc)

    def save(self, plugin_name: str) -> None:
        """Save current values for one plugin directly to JSON."""
        path = self._json_path(plugin_name)
        if path is None:
            log.settings("save skipped — no config_dir", plugin=plugin_name)
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        values = self.dump_values(plugin_name)
        try:
            with path.open("w", encoding="utf-8") as f:
                json.dump(values, f, indent=2, ensure_ascii=False)
            log.settings("saved", plugin=plugin_name, path=path)
        except Exception as exc:
            log.warning("Could not save settings for %r: %s", plugin_name, exc)

