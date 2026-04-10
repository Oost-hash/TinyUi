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

"""Widget config store for runtime V2 persistence."""

from __future__ import annotations

import json

from runtimeV2.contracts import PersistencePaths, WidgetInstanceConfig


class WidgetConfigStore:
    """Store widget configuration values for one config set."""

    WIDGETS_FILE = "widgets.json"
    VISIBILITY_FILE = "widget_visibility.json"

    def __init__(self, paths: PersistencePaths, active_set: str) -> None:
        self._paths = paths
        self._active_set = active_set

    def load_for_overlay(self, overlay_id: str) -> list[WidgetInstanceConfig]:
        """Load widget configuration for an overlay."""

        path = self._widgets_path(overlay_id)
        if not path.exists():
            return []
        data = json.loads(path.read_text(encoding="utf-8"))
        return [WidgetInstanceConfig.from_dict(item) for item in data.get("widgets", [])]

    def save_for_overlay(self, overlay_id: str, configs: list[WidgetInstanceConfig]) -> None:
        """Save widget configuration for an overlay."""

        path = self._widgets_path(overlay_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(
                {"version": 1, "widgets": [config.to_dict() for config in configs]},
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

    def get_widget(self, overlay_id: str, widget_id: str) -> WidgetInstanceConfig | None:
        """Return one widget config."""

        for config in self.load_for_overlay(overlay_id):
            if config.widget_id == widget_id:
                return config
        return None

    def set_widget_enabled(self, overlay_id: str, widget_id: str, enabled: bool) -> bool:
        """Set widget enabled state."""

        configs = self.load_for_overlay(overlay_id)
        for config in configs:
            if config.widget_id == widget_id:
                config.enabled = enabled
                self.save_for_overlay(overlay_id, configs)
                return True
        configs.append(WidgetInstanceConfig(widget_id=widget_id, enabled=enabled))
        self.save_for_overlay(overlay_id, configs)
        return True

    def set_widget_position(self, overlay_id: str, widget_id: str, x: int, y: int) -> bool:
        """Set widget position."""

        configs = self.load_for_overlay(overlay_id)
        for config in configs:
            if config.widget_id == widget_id:
                config.position = (x, y)
                self.save_for_overlay(overlay_id, configs)
                return True
        configs.append(WidgetInstanceConfig(widget_id=widget_id, position=(x, y)))
        self.save_for_overlay(overlay_id, configs)
        return True

    def set_widget_values(self, overlay_id: str, widget_id: str, values: dict[str, object]) -> bool:
        """Set widget config values."""

        configs = self.load_for_overlay(overlay_id)
        for config in configs:
            if config.widget_id == widget_id:
                config.values.update(values)
                self.save_for_overlay(overlay_id, configs)
                return True
        configs.append(WidgetInstanceConfig(widget_id=widget_id, values=dict(values)))
        self.save_for_overlay(overlay_id, configs)
        return True

    def reset_widget_values(self, overlay_id: str, widget_id: str) -> bool:
        """Reset widget config values to empty."""

        configs = self.load_for_overlay(overlay_id)
        for config in configs:
            if config.widget_id == widget_id:
                config.values = {}
                self.save_for_overlay(overlay_id, configs)
                return True
        return False

    def get_global_visible(self) -> bool:
        """Return the global widget visibility flag."""

        path = self._visibility_path()
        if not path.exists():
            return True
        data = json.loads(path.read_text(encoding="utf-8"))
        return bool(data.get("global_visible", True))

    def set_global_visible(self, visible: bool) -> None:
        """Store the global widget visibility flag."""

        path = self._visibility_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(
                {"version": 1, "global_visible": visible},
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

    def _widgets_path(self, overlay_id: str):
        return self._paths.namespace_dir(self._active_set, overlay_id) / self.WIDGETS_FILE

    def _visibility_path(self):
        return self._paths.config_set_dir(self._active_set) / self.VISIBILITY_FILE
