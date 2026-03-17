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

"""Loader for widget configs — one JSON file per widget.

Directory layout:
    widgets/
        battery.json
        brake_bias.json
        relative.json
        ...

Each file contains a single widget's structured config (to_dict format).
"""

from __future__ import annotations

import importlib
import json
from pathlib import Path
from typing import Any

from tinycore.config import read_json, write_json
from plugins.tinypedal.models.base import WidgetConfig


def _load_widget_class(widget_name: str) -> type[WidgetConfig]:
    """Dynamically import a widget class by module name.

    e.g. 'battery' → from plugins.tinypedal.models.widgets.battery import Battery
    """
    module = importlib.import_module(f"plugins.tinypedal.models.widgets.{widget_name}")
    # class name is PascalCase of the module name
    class_name = widget_name.replace("_", " ").title().replace(" ", "")
    return getattr(module, class_name)


class WidgetLoader:
    """Load/save individual widget configs from a directory of JSON files.

    Each widget gets its own file: {widget_name}.json
    """

    def load(self, path: Path) -> dict[str, WidgetConfig]:
        """Load all widget JSON files from directory.

        Missing files get default instances.
        """
        widgets = {}

        # discover all known widget modules
        models_dir = Path(__file__).parent.parent / "models" / "widgets"
        for module_file in sorted(models_dir.glob("*.py")):
            if module_file.stem == "__init__":
                continue

            widget_name = module_file.stem
            widget_cls = _load_widget_class(widget_name)
            json_path = path / f"{widget_name}.json"

            if json_path.exists():
                data = read_json(json_path)
                widgets[widget_name] = widget_cls.from_dict(data)
            else:
                widgets[widget_name] = widget_cls()

        return widgets

    def save(self, path: Path, config: dict[str, WidgetConfig]) -> None:
        """Save each widget to its own JSON file."""
        path.mkdir(parents=True, exist_ok=True)
        for widget_name, widget in config.items():
            write_json(path / f"{widget_name}.json", widget.to_dict())

    def save_one(self, path: Path, widget_name: str, widget: WidgetConfig) -> None:
        """Save a single widget — no lock needed on other files."""
        path.mkdir(parents=True, exist_ok=True)
        write_json(path / f"{widget_name}.json", widget.to_dict())
