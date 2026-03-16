"""Concrete config loaders — one per config type."""

from .heatmap_loader import HeatmapLoader
from .preset_loaders import BrakePresetLoader, ClassPresetLoader, CompoundPresetLoader
from .global_loader import GlobalConfigLoader
from .widget_loader import WidgetLoader

__all__ = [
    "HeatmapLoader",
    "BrakePresetLoader",
    "ClassPresetLoader",
    "CompoundPresetLoader",
    "GlobalConfigLoader",
    "WidgetLoader",
]
