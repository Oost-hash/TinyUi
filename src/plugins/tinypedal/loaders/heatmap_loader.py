"""Loader for heatmap configs — dict[str, HeatmapConfig]."""

from pathlib import Path

from tinycore.config import read_json, write_json
from plugins.tinypedal.models.base import HeatmapConfig


class HeatmapLoader:
    """Load/save heatmap configs as structured JSON."""

    def load(self, path: Path) -> dict[str, HeatmapConfig]:
        data = read_json(path)
        return {
            name: HeatmapConfig.from_dict(name, entry)
            for name, entry in data.items()
        }

    def save(self, path: Path, config: dict[str, HeatmapConfig]) -> None:
        data = {name: hm.to_dict() for name, hm in config.items()}
        write_json(path, data)
