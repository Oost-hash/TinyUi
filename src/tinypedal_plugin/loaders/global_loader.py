"""Loader for global config sections — application, telemetry, etc."""

from pathlib import Path

from tinycore.config import read_json, write_json
from tinypedal_plugin.models.tinypedal_global_config import (
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
