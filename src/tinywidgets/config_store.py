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
"""WidgetConfigStore — persists all user-editable widget config to JSON.

Saved per plugin in:
  <config_dir>/<plugin_name>/widget-config.json

Format:
  {
    "fuel": {
      "x": 100, "y": 200,
      "enable": true,
      "label": "FUEL",
      "flash_below": 2.0,
      "thresholds": [{"value": 0.0, "color": "#FF4444"}, ...]
    }
  }
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

_log = logging.getLogger(__name__)


class WidgetConfigStore:
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
            "enable":     enable,
            "x":          x,
            "y":          y,
            "label":      label,
            "thresholds": thresholds,
        }
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            with self._path.open("w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2)
        except OSError as exc:
            _log.warning("Could not save widget config: %s", exc)

    def _load(self) -> dict:
        try:
            with self._path.open(encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
