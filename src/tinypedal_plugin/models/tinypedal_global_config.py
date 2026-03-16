# Auto-generated global configuration

from dataclasses import dataclass
from typing import Any, Dict

from .base import FlatMixin


@dataclass
class ApplicationConfig(FlatMixin):
    show_at_startup: bool = True
    check_for_updates_on_startup: bool = True
    remember_position: bool = True
    remember_size: bool = True
    enable_high_dpi_scaling: bool = True
    enable_auto_load_preset: bool = False
    enable_global_hotkey: bool = False
    show_confirmation_for_batch_toggle: bool = True
    snap_distance: int = 10
    snap_gap: int = 0
    grid_move_size: int = 8
    minimum_update_interval: int = 10
    maximum_saving_attempts: int = 10
    position_x: int = 0
    position_y: int = 0
    window_width: int = 0
    window_height: int = 0
    window_color_theme: str = 'Dark'


@dataclass
class CompatibilityConfig(FlatMixin):
    enable_translucent_background: bool = True
    enable_window_position_correction: bool = True
    global_bkg_color: str = '#000000'
    multimedia_plugin_on_windows: str = 'WMF'


@dataclass
class NotificationConfig(FlatMixin):
    notify_locked_preset: bool = True
    font_color_locked_preset: str = '#FFFFFF'
    bkg_color_locked_preset: str = '#777777'
    notify_spectate_mode: bool = True
    font_color_spectate_mode: str = '#FFFFFF'
    bkg_color_spectate_mode: str = '#0088CC'
    notify_pace_notes_playback: bool = True
    font_color_pace_notes_playback: str = '#FFFFFF'
    bkg_color_pace_notes_playback: str = '#228800'
    notify_global_hotkey: bool = True
    font_color_global_hotkey: str = '#FFFFFF'
    bkg_color_global_hotkey: str = '#885544'
    notify_auto_backup_car_setup: bool = True
    font_color_auto_backup_car_setup: str = '#FFFFFF'
    bkg_color_auto_backup_car_setup: str = '#334499'


@dataclass
class TelemetryConfig(FlatMixin):
    api_name: str = 'API_DEFAULT_NAME'
    enable_api_selection_from_preset: bool = True
    enable_auto_backup_car_setup: bool = False


@dataclass
class TrackMapViewerConfig(FlatMixin):
    inner_margin: int = 6
    position_increment_step: int = 5
    font_color_light: str = '#CCCCCC'
    font_color_dark: str = '#333333'
    bkg_color_light: str = '#FFFFFF'
    bkg_color_dark: str = '#333333'
    map_color: str = '#FFFFFF'
    map_width: int = 10
    map_outline_color: str = '#111111'
    map_outline_width: int = 4
    start_line_color: str = '#FF4400'
    start_line_width: int = 10
    start_line_length: int = 30
    sector_line_color: str = '#00AAFF'
    sector_line_width: int = 8
    sector_line_length: int = 30
    marked_coordinates_color: str = '#808080'
    marked_coordinates_size: int = 15
    highlighted_coordinates_color: str = '#22DD00'
    highlighted_coordinates_width: int = 5
    highlighted_coordinates_size: int = 15
    center_mark_color: str = '#808080'
    center_mark_width: int = 1
    center_mark_radius: int = 1000
    curve_section_color: str = '#FF4400'
    curve_section_width: int = 5
    osculating_circle_color: str = '#00AAFF'
    osculating_circle_width: int = 2
    distance_circle_color: str = '#808080'
    distance_circle_width: int = 1
    distance_circle_0_radius: int = 50
    distance_circle_1_radius: int = 100
    distance_circle_2_radius: int = 200
    distance_circle_3_radius: int = 300
    distance_circle_4_radius: int = 400
    distance_circle_5_radius: int = 500
    distance_circle_6_radius: int = 1000
    distance_circle_7_radius: int = 0
    distance_circle_8_radius: int = 0
    distance_circle_9_radius: int = 0
    curve_grade_hairpin: int = 5
    curve_grade_1: int = 15
    curve_grade_2: int = 25
    curve_grade_3: int = 40
    curve_grade_4: int = 65
    curve_grade_5: int = 105
    curve_grade_6: int = 275
    curve_grade_7: int = -1
    curve_grade_8: int = -1
    curve_grade_straight: int = 3050
    length_grade_short: int = 0
    length_grade_normal: int = 50
    length_grade_long: int = 150
    length_grade_very_long: int = 250
    length_grade_extra_long: int = 350
    length_grade_extremely_long: int = 450
    slope_grade_flat: int = 0
    slope_grade_gentle: float = 0.03
    slope_grade_moderate: float = 0.1
    slope_grade_steep: float = 0.25
    slope_grade_extreme: float = 0.5
    slope_grade_cliff: int = 1


@dataclass
class UserPathConfig(FlatMixin):
    settings_path: str = 'settings/'
    brand_logo_path: str = 'brandlogo/'
    delta_best_path: str = 'deltabest/'
    sector_best_path: str = 'deltabest/'
    energy_delta_path: str = 'deltabest/'
    fuel_delta_path: str = 'deltabest/'
    track_map_path: str = 'trackmap/'
    pace_notes_path: str = 'pacenotes/'
    track_notes_path: str = 'tracknotes/'
    car_setups_path: str = 'carsetups/'


GLOBAL: Dict[str, FlatMixin] = {
    'application': ApplicationConfig(),
    'compatibility': CompatibilityConfig(),
    'notification': NotificationConfig(),
    'telemetry': TelemetryConfig(),
    'track_map_viewer': TrackMapViewerConfig(),
    'user_path': UserPathConfig(),
}
