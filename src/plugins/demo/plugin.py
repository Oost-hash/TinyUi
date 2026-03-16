"""DemoPlugin — sample data + editor registrations for development.

This is the reference example of how a plugin works:
1. Provide default config data (written to JSON if files don't exist)
2. Provide editors.toml (declares what editors the UI should offer)

The plugin only provides data — tinycore handles loading, saving, and paths.
Config files live in: data/plugin-config/demo/
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from tinycore.editor import load_editors_toml

if TYPE_CHECKING:
    from tinycore.app import App


# --- Default data (used when JSON files don't exist yet) ---

DEFAULT_HEATMAPS = {
    "HEATMAP_DEFAULT_BRAKE": {
        "entries": [
            {"temperature": -273.0, "color": "#44F"},
            {"temperature": 100.0, "color": "#48F"},
            {"temperature": 200.0, "color": "#4FF"},
            {"temperature": 400.0, "color": "#4F4"},
            {"temperature": 600.0, "color": "#FF4"},
            {"temperature": 800.0, "color": "#F44"},
        ],
    },
    "HEATMAP_DEFAULT_TYRE": {
        "entries": [
            {"temperature": -273.0, "color": "#44F"},
            {"temperature": 60.0, "color": "#F4F"},
            {"temperature": 80.0, "color": "#F48"},
            {"temperature": 100.0, "color": "#F44"},
            {"temperature": 120.0, "color": "#F84"},
            {"temperature": 140.0, "color": "#FF4"},
        ],
    },
}

DEFAULT_COMPOUNDS = {
    "Dry": {"symbol": "D", "heatmap": "HEATMAP_DEFAULT_TYRE"},
    "Wet": {"symbol": "W", "heatmap": "HEATMAP_DEFAULT_TYRE"},
    "Intermediate": {"symbol": "I", "heatmap": "HEATMAP_DEFAULT_TYRE"},
}


class DemoPlugin:
    """Development plugin — registers config + editors via TOML."""

    name = "demo"

    def register(self, app: App) -> None:
        # 1. Register config files with defaults
        app.loaders.register("heatmaps", "heatmaps.json", self.name, DEFAULT_HEATMAPS)
        app.loaders.register("compounds", "compounds.json", self.name, DEFAULT_COMPOUNDS)

        # 2. Load from disk (creates JSON from defaults if missing)
        app.loaders.load_all(app.config)

        # 3. Load editor specs from editors.toml (lives with plugin source)
        editors_path = Path(__file__).parent / "editors.toml"
        for spec in load_editors_toml(editors_path):
            app.editors.register(spec)

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass
