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

"""WidgetConfigStore — manages widget instance configuration."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from runtime.persistence.paths import ConfigResolver


@dataclass
class WidgetInstanceConfig:
    """Configuration of one widget instance."""

    widget_id: str
    enabled: bool = True
    position: tuple[int, int] = field(default_factory=lambda: (0, 0))
    values: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "widget_id": self.widget_id,
            "enabled": self.enabled,
            "position": list(self.position),
            "values": self.values,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "WidgetInstanceConfig":
        """Create from dictionary."""
        pos = data.get("position", [0, 0])
        return cls(
            widget_id=data["widget_id"],
            enabled=data.get("enabled", True),
            position=(pos[0], pos[1]) if len(pos) >= 2 else (0, 0),
            values=data.get("values", {}),
        )


class WidgetConfigStore:
    """Manages widget configuration per overlay."""

    WIDGETS_FILE = "widgets.json"

    def __init__(self, resolver: ConfigResolver, config_set_id: str) -> None:
        self._resolver = resolver
        self._set_id = config_set_id

    def _widgets_path(self, overlay_id: str) -> Path:
        """Path to widgets.json for an overlay."""
        return (
            self._resolver.namespace_dir(self._set_id, overlay_id)
            / self.WIDGETS_FILE
        )

    def load_for_overlay(self, overlay_id: str) -> list[WidgetInstanceConfig]:
        """Load widget configuration for an overlay."""
        path = self._widgets_path(overlay_id)
        if not path.exists():
            return []

        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            widgets = data.get("widgets", [])
            return [WidgetInstanceConfig.from_dict(w) for w in widgets]
        except Exception:
            return []

    def save_for_overlay(
        self,
        overlay_id: str,
        configs: list[WidgetInstanceConfig],
    ) -> None:
        """Save widget configuration for an overlay."""
        path = self._widgets_path(overlay_id)
        path.parent.mkdir(parents=True, exist_ok=True)

        data: dict[str, Any] = {
            "version": 1,
            "widgets": [c.to_dict() for c in configs],
        }
        path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def update_widget(
        self,
        overlay_id: str,
        widget_id: str,
        values: dict[str, Any],
    ) -> bool:
        """Update specific widget values."""
        configs = self.load_for_overlay(overlay_id)
        for config in configs:
            if config.widget_id == widget_id:
                config.values.update(values)
                self.save_for_overlay(overlay_id, configs)
                return True
        return False

    def get_widget(self, overlay_id: str, widget_id: str) -> WidgetInstanceConfig | None:
        """Get configuration for a specific widget."""
        configs = self.load_for_overlay(overlay_id)
        for config in configs:
            if config.widget_id == widget_id:
                return config
        return None

    def set_widget_enabled(
        self,
        overlay_id: str,
        widget_id: str,
        enabled: bool,
    ) -> bool:
        """Enable or disable a specific widget."""
        configs = self.load_for_overlay(overlay_id)
        for config in configs:
            if config.widget_id == widget_id:
                config.enabled = enabled
                self.save_for_overlay(overlay_id, configs)
                return True
        return False

    def set_widget_position(
        self,
        overlay_id: str,
        widget_id: str,
        x: int,
        y: int,
    ) -> bool:
        """Set position for a specific widget."""
        configs = self.load_for_overlay(overlay_id)
        for config in configs:
            if config.widget_id == widget_id:
                config.position = (x, y)
                self.save_for_overlay(overlay_id, configs)
                return True
        return False
