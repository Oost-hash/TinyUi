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
"""DemoPlugin — consumer-side development plugin.

The demo plugin is intended to become the reference shape for a consumer-side
plugin:
1. register local config data
2. register editor definitions
3. provide widget-facing assets such as widgets

It no longer owns a connector in its manifest. Runtime data should come from
required capabilities instead of plugin-owned data sources.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from tinyui_schema import load_editors_toml

if TYPE_CHECKING:
    from tinycore.plugin.context import PluginContext


# --- Default data (used when JSON files don't exist yet) ---

DEFAULT_HEATMAPS = {
    "HEATMAP_DEFAULT_BRAKE": {
        "entries": [
            {"temperature": -273.0, "color": "#44F"},
            {"temperature": 100.0, "color": "#48F"},
            {"temperature": 200.0, "color": "#4FF"},
            {"temperature": 400.0, "color": "#4F4"},
            {"temperature": 600.0, "color": "#FF4"},
            {"temperature": 800.0, "color": "#F44"},
        ],
    },
    "HEATMAP_DEFAULT_TYRE": {
        "entries": [
            {"temperature": -273.0, "color": "#44F"},
            {"temperature": 60.0, "color": "#F4F"},
            {"temperature": 80.0, "color": "#F48"},
            {"temperature": 100.0, "color": "#F44"},
            {"temperature": 120.0, "color": "#F84"},
            {"temperature": 140.0, "color": "#FF4"},
        ],
    },
}

DEFAULT_COMPOUNDS = {
    "Dry": {"symbol": "D", "heatmap": "HEATMAP_DEFAULT_TYRE"},
    "Wet": {"symbol": "W", "heatmap": "HEATMAP_DEFAULT_TYRE"},
    "Intermediate": {"symbol": "I", "heatmap": "HEATMAP_DEFAULT_TYRE"},
}


class DemoPlugin:
    """Development consumer plugin — registers config and editors."""

    name = "demo"

    def register(self, ctx: PluginContext) -> None:
        ctx.config.register("heatmaps",  "heatmaps.json",  DEFAULT_HEATMAPS)
        ctx.config.register("compounds", "compounds.json", DEFAULT_COMPOUNDS)
        ctx.config.load_all()

        plugin_dir = Path(__file__).parent
        for spec in load_editors_toml(plugin_dir / "editors" / "editors.toml"):
            ctx.editors.register(spec)

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass
