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

"""Default widget definitions available to overlays."""

from __future__ import annotations

from widget_api.contracts import WidgetDefinition
from widget_api.registry import WidgetRegistry


DEFAULT_WIDGET_DEFINITIONS: tuple[WidgetDefinition, ...] = (
    WidgetDefinition(
        widget="textWidget",
        display_name="Text Widget",
        description="Displays a label with a single bound text source.",
        required_bindings=("source",),
    ),
)


def create_default_widget_registry() -> WidgetRegistry:
    """Build a registry seeded with platform default widget kinds."""

    return WidgetRegistry(DEFAULT_WIDGET_DEFINITIONS)
