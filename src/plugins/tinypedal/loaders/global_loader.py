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

"""Loader for global config sections — application, telemetry, etc."""

from pathlib import Path

from tinycore.config import read_json, write_json
from plugins.tinypedal.models.tinypedal_global_config import (
    ApplicationConfig,
    CompatibilityConfig,
    NotificationConfig,
    TelemetryConfig,
    UserPathConfig,
)


class GlobalConfigLoader:
    """Load/save global config as structured JSON.

    Stores all global sections in one file:
    {
        "application": {...},
        "compatibility": {...},
        "telemetry": {...},
        "notification": {...},
        "user_path": {...}
    }
    """

    SECTION_CLASSES = {
        "application": ApplicationConfig,
        "compatibility": CompatibilityConfig,
        "notification": NotificationConfig,
        "telemetry": TelemetryConfig,
        "user_path": UserPathConfig,
    }

    def load(self, path: Path) -> dict[str, object]:
        data = read_json(path)
        result = {}
        for section, cls in self.SECTION_CLASSES.items():
            section_data = data.get(section, {})
            result[section] = cls.from_dict(section_data)
        return result

    def save(self, path: Path, config: dict[str, object]) -> None:
        data = {}
        for section, obj in config.items():
            if hasattr(obj, "to_dict"):
                data[section] = obj.to_dict()
        write_json(path, data)
