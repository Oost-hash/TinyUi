"""DemoPlugin — sample data + editor registrations for development.

This is the reference example of how a plugin declares:
1. Config data (what goes in the ConfigStore)
2. Editor specs (what editors the UI should offer)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from tinycore.editor import ColumnDef, EditorSpec

if TYPE_CHECKING:
    from tinycore.app import App


# --- Sample data ---

SAMPLE_HEATMAPS = {
    "HEATMAP_DEFAULT_BRAKE": {
        "0": "#4444FF",
        "200": "#44AAFF",
        "400": "#44FF44",
        "600": "#FFAA44",
        "800": "#FF4444",
    },
    "HEATMAP_DEFAULT_TYRE": {
        "50": "#4444FF",
        "70": "#44AAFF",
        "85": "#44FF44",
        "100": "#FFAA44",
        "120": "#FF4444",
    },
    "HEATMAP_RAIN": {
        "30": "#2244AA",
        "50": "#4488CC",
        "70": "#66BBEE",
        "90": "#AADDFF",
    },
}

SAMPLE_BRAKES = {
    "Default": {
        "failure_thickness": "0.0",
        "heatmap": "HEATMAP_DEFAULT_BRAKE",
    },
    "Carbon Ceramic": {
        "failure_thickness": "2.5",
        "heatmap": "HEATMAP_DEFAULT_BRAKE",
    },
}


# --- Config keys (used as type keys in ConfigStore) ---

class HeatmapData:
    """Type key for heatmap config in the store."""

class BrakeData:
    """Type key for brake preset config in the store."""


# --- Editor specs ---

HEATMAP_EDITOR = EditorSpec(
    id="heatmap",
    title="Heatmap Editor",
    config_key=HeatmapData,
    columns=[
        ColumnDef("temperature", float, default_value=0.0),
        ColumnDef("color", str, default_value="#FFFFFF"),
    ],
)

BRAKE_EDITOR = EditorSpec(
    id="brake_preset",
    title="Brake Preset Editor",
    config_key=BrakeData,
    columns=[
        ColumnDef("failure_thickness", float, default_value=0.0),
        ColumnDef("heatmap", str, default_value="HEATMAP_DEFAULT_BRAKE"),
    ],
)


class DemoPlugin:
    """Development plugin — seeds config store and registers editors."""

    name = "demo"

    def register(self, app: App) -> None:
        # 1. Seed data into config store
        app.config.update(HeatmapData, SAMPLE_HEATMAPS)
        app.config.update(BrakeData, SAMPLE_BRAKES)

        # 2. Register editors — UI will pick these up automatically
        app.editors.register(HEATMAP_EDITOR)
        app.editors.register(BRAKE_EDITOR)

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass
