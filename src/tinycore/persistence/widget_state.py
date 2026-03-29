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

"""Host-owned widget state persistence."""

from __future__ import annotations

import json
from pathlib import Path

from tinyruntime_schema import get_logger

_log = get_logger(__name__)


class WidgetStateStore:
    """Loads and saves all user-editable config for one plugin's widgets."""

    _FILENAME = "widget-config.json"

    def __init__(self, config_dir: Path, plugin_name: str) -> None:
        self._path = config_dir / plugin_name / self._FILENAME
        self._data: dict[str, dict] = self._load()

    def get(self, widget_id: str) -> dict | None:
        """Return the saved config dict for widget_id, or None if not stored."""
        return self._data.get(widget_id)

    def save(
        self,
        widget_id: str,
        enable: bool,
        x: int,
        y: int,
        label: str,
        thresholds: list[dict],
    ) -> None:
        """Persist all user-editable fields for widget_id."""
        self._data[widget_id] = {
            "enable": enable,
            "x": x,
            "y": y,
            "label": label,
            "thresholds": thresholds,
        }
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            with self._path.open("w", encoding="utf-8") as file_obj:
                json.dump(self._data, file_obj, indent=2, ensure_ascii=False)
                file_obj.write("\n")
        except OSError as exc:
            _log.warning("Could not save widget config: %s", exc)

    def _load(self) -> dict:
        try:
            with self._path.open(encoding="utf-8") as file_obj:
                return json.load(file_obj)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}


class WidgetStateRegistry:
    """Factory for plugin-scoped widget state stores."""

    def __init__(self, config_dir: Path | None = None) -> None:
        self._config_dir = config_dir

    def for_plugin(self, plugin_name: str) -> WidgetStateStore | None:
        """Return the widget state store for one plugin, if persistence is enabled."""
        if self._config_dir is None:
            return None
        return WidgetStateStore(self._config_dir, plugin_name)
