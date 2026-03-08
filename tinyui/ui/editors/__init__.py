"""Editors package."""

# Base classes (split from _editor_common.py)
from ._base_editor import (
    BaseEditor,
    TableEditor,
    editor_button_bar,
)

# Dialog helpers
from ._editor_common import (
    BatchOffset,
    TableBatchReplace,
)

# Generic dict-based table editor
from ._generic_dict_editor import GenericDictTableEditor

# Concrete editors
from .brake_editor import BrakeEditor
from .config import FontConfig, UserConfig
from .driver_stats_viewer import DriverStatsViewer
from .fuel_calculator import FuelCalculator
from .heatmap_editor import HeatmapEditor
from .preset_transfer import PresetTransfer
from .track_info_editor import TrackInfoEditor
from .track_notes_editor import TrackNotesEditor
from .tyre_compound_editor import TyreCompoundEditor
from .vehicle_brand_editor import VehicleBrandEditor
from .vehicle_class_editor import VehicleClassEditor

__all__ = [
    # Base classes
    "BaseEditor",
    "TableEditor",
    "GenericDictTableEditor",
    "editor_button_bar",
    "BatchOffset",
    "TableBatchReplace",
    # Concrete editors
    "BrakeEditor",
    "DriverStatsViewer",
    "FontConfig",
    "FuelCalculator",
    "HeatmapEditor",
    "PresetTransfer",
    "TrackInfoEditor",
    "TrackNotesEditor",
    "TyreCompoundEditor",
    "UserConfig",
    "VehicleBrandEditor",
    "VehicleClassEditor",
]
