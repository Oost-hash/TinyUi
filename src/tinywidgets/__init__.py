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
"""tinywidgets — self-contained overlay widget system."""

from .context import WidgetContext, WidgetModel, WidgetOverlayState
from .flash import FlashState
from .overlay import WidgetOverlay
from .registry import WidgetRegistry
from .runner import ProviderUpdater, TextWidgetRunner, WidgetState
from .spec import WidgetSpec, load_widgets_toml
from .threshold import ThresholdEntry, evaluate

__all__ = [
    "FlashState",
    "ProviderUpdater",
    "TextWidgetRunner",
    "ThresholdEntry",
    "WidgetContext",
    "WidgetModel",
    "WidgetOverlayState",
    "WidgetOverlay",
    "WidgetRegistry",
    "WidgetSpec",
    "WidgetState",
    "evaluate",
    "load_widgets_toml",
]
