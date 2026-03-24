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
"""WidgetSpec — declarative overlay widget definition.

Plugins load these from widgets.toml and pass them to the WidgetRegistry.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .threshold import ThresholdEntry


@dataclass
class WidgetSpec:
    """Declares an overlay widget that a plugin provides."""

    # Identity
    id:          str
    title:       str
    description: str  = ""
    enable:      bool = True

    # Telemetry
    source: str = ""   # dot-path into connector, e.g. "vehicle.fuel"
    format: str = "{}" # Python format string applied to the raw value
    label:  str = ""   # short label shown above or next to the value

    # Position on the overlay (logical pixels)
    x: int = 100
    y: int = 100

    # Threshold coloring — each entry has an upper bound; flash per entry
    thresholds: list[ThresholdEntry] = field(default_factory=list)

    # Flash target — which part of the widget blinks (speed is per ThresholdEntry)
    flash_target: str = "value"  # "value" | "text" | "widget"


def load_widgets_toml(path: Path) -> list[WidgetSpec]:
    """Load widget specs from a widgets.toml file."""
    import tomllib

    with open(path, "rb") as f:
        data = tomllib.load(f)

    specs: list[WidgetSpec] = []
    for widget_id, widget_data in data.items():
        raw_thresholds = widget_data.get("thresholds", [])
        thresholds = [
            ThresholdEntry(
                value       = t["value"],
                color       = t["color"],
                flash       = t.get("flash", False),
                flash_speed = t.get("flash_speed", 5),
            )
            for t in raw_thresholds
        ]
        specs.append(WidgetSpec(
            id           = widget_id,
            title        = widget_data.get("title", widget_id),
            description  = widget_data.get("description", ""),
            enable       = widget_data.get("enable", True),
            source       = widget_data.get("source", ""),
            format       = widget_data.get("format", "{}"),
            label        = widget_data.get("label", ""),
            x            = widget_data.get("x", 100),
            y            = widget_data.get("y", 100),
            thresholds   = thresholds,
            flash_target = widget_data.get("flash_target", "value"),
        ))
    return specs
