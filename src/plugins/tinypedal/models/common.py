# Auto-generated common configuration

from dataclasses import dataclass
from typing import Any, Dict

from .base import FlatMixin


@dataclass
class OverlayConfig(FlatMixin):
    fixed_position: bool = False
    auto_hide: bool = True
    enable_grid_move: bool = False
    vr_compatibility: bool = False


@dataclass
class PaceNotesPlaybackConfig(FlatMixin):
    enable: bool = False
    update_interval: int = 10
    enable_playback_while_in_pit: bool = False
    enable_manual_file_selector: bool = False
    pace_notes_file_name: str = ''
    pace_notes_sound_path: str = '/'
    pace_notes_sound_format: str = 'wav'
    pace_notes_sound_volume: int = 50
    pace_notes_sound_max_duration: int = 10
    pace_notes_sound_max_queue: int = 5
    pace_notes_global_offset: int = 0


@dataclass
class PresetConfig(FlatMixin):
    api_name: str = 'API_DEFAULT_NAME'
    version: str = '__version__'


@dataclass
class UnitsConfig(FlatMixin):
    distance_unit: str = 'Meter'
    fuel_unit: str = 'Liter'
    odometer_unit: str = 'Kilometer'
    power_unit: str = 'Kilowatt'
    speed_unit: str = 'KPH'
    temperature_unit: str = 'Celsius'
    turbo_pressure_unit: str = 'bar'
    tyre_pressure_unit: str = 'kPa'


COMMON: Dict[str, FlatMixin] = {
    'overlay': OverlayConfig(),
    'pace_notes_playback': PaceNotesPlaybackConfig(),
    'preset': PresetConfig(),
    'units': UnitsConfig(),
}
