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

"""TinyPedalPlugin — registers all TinyPedal config types with tinycore."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tinycore.app import App


class TinyPedalPlugin:
    """Plugin that registers TinyPedal-specific loaders and models."""

    name = "tinypedal"

    def __init__(self, config_dir: Path):
        self._config_dir = config_dir

    def register(self, app: App) -> None:
        from plugins.tinypedal.loaders import (
            BrakePresetLoader,
            ClassPresetLoader,
            CompoundPresetLoader,
            GlobalConfigLoader,
            HeatmapLoader,
            WidgetLoader,
        )
        from plugins.tinypedal.models.base import (
            BrakePreset,
            ClassPreset,
            CompoundPreset,
            HeatmapConfig,
            WidgetConfig,
        )

        app.loaders.register(
            dict[str, BrakePreset],
            BrakePresetLoader(),
            self._config_dir / "brakes.json",
        )
        app.loaders.register(
            dict[str, ClassPreset],
            ClassPresetLoader(),
            self._config_dir / "classes.json",
        )
        app.loaders.register(
            dict[str, CompoundPreset],
            CompoundPresetLoader(),
            self._config_dir / "compounds.json",
        )
        app.loaders.register(
            dict[str, HeatmapConfig],
            HeatmapLoader(),
            self._config_dir / "heatmap.json",
        )
        app.loaders.register(
            dict[str, object],
            GlobalConfigLoader(),
            self._config_dir / "global.json",
        )
        app.loaders.register(
            dict[str, WidgetConfig],
            WidgetLoader(),
            self._config_dir / "widgets",
        )

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass
