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
"""Demo2Plugin — second sample plugin for testing plugin switching."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from tinycore.settings import SettingsSpec
from tinycore.widget import load_widgets_toml

if TYPE_CHECKING:
    from tinycore.plugin.context import PluginContext


class Demo2Plugin:
    """Second demo plugin — lap timing widgets and settings."""

    name = "demo2"

    def register(self, ctx: PluginContext) -> None:
        plugin_dir = Path(__file__).parent
        for spec in load_widgets_toml(plugin_dir / "widgets.toml"):
            ctx.widgets.register(spec)

        _r = ctx.settings.register

        _r(SettingsSpec(
            key="show_sector_times", label="Show sector times", type="bool",
            default=True, description="Show individual sector times",
            section="Display",
        ))
        _r(SettingsSpec(
            key="time_format", label="Time format", type="enum",
            default="mm:ss.ms", options=["mm:ss.ms", "ss.ms"],
            description="Format for lap time display",
            section="Display",
        ))
        _r(SettingsSpec(
            key="delta_range", label="Delta range (s)", type="float",
            default=2.0, min=0.5, max=10.0, step=0.5,
            description="Maximum delta shown on the bar",
            section="Display",
        ))

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass
