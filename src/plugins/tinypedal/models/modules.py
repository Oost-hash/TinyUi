# Auto-generated module configuration

from dataclasses import dataclass
from typing import Any, Dict

from .base import FlatMixin


@dataclass
class ModuleDeltaConfig(FlatMixin):
    enable: bool = True
    update_interval: int = 10
    idle_update_interval: int = 400
    minimum_delta_distance: int = 5
    delta_smoothing_samples: int = 30
    laptime_pace_samples: int = 6
    laptime_pace_margin: int = 5


@dataclass
class ModuleForceConfig(FlatMixin):
    enable: bool = True
    update_interval: int = 10
    idle_update_interval: int = 400
    gravitational_acceleration: float = 9.80665
    max_g_force_reset_delay: int = 5
    max_average_g_force_samples: int = 10
    max_average_g_force_difference: float = 0.2
    max_average_g_force_reset_delay: int = 30
    max_braking_rate_reset_delay: int = 60


@dataclass
class ModuleFuelConfig(FlatMixin):
    enable: bool = True
    update_interval: int = 10
    idle_update_interval: int = 400
    minimum_delta_distance: int = 5


@dataclass
class ModuleHybridConfig(FlatMixin):
    enable: bool = True
    update_interval: int = 10
    idle_update_interval: int = 400
    minimum_delta_distance: int = 5


@dataclass
class ModuleMappingConfig(FlatMixin):
    enable: bool = True
    update_interval: int = 10
    idle_update_interval: int = 400


@dataclass
class ModuleNotesConfig(FlatMixin):
    enable: bool = True
    update_interval: int = 10
    idle_update_interval: int = 400


@dataclass
class ModuleRelativeConfig(FlatMixin):
    enable: bool = True
    update_interval: int = 100
    idle_update_interval: int = 400


@dataclass
class ModuleSectorsConfig(FlatMixin):
    enable: bool = True
    update_interval: int = 10
    idle_update_interval: int = 400
    enable_all_time_best_sectors: bool = True


@dataclass
class ModuleStatsConfig(FlatMixin):
    enable: bool = True
    update_interval: int = 200
    idle_update_interval: int = 400
    vehicle_classification: str = 'Class - Brand'
    enable_podium_by_class: bool = True


@dataclass
class ModuleStintConfig(FlatMixin):
    enable: bool = True
    update_interval: int = 100
    idle_update_interval: int = 400
    minimum_stint_threshold_minutes: int = 10
    minimum_pitstop_threshold_seconds: int = 3
    minimum_tyre_temperature_threshold: int = 55


@dataclass
class ModuleVehiclesConfig(FlatMixin):
    enable: bool = True
    update_interval: int = 10
    idle_update_interval: int = 400
    lap_difference_ahead_threshold: float = 0.9
    lap_difference_behind_threshold: float = 0.9


@dataclass
class ModuleWheelsConfig(FlatMixin):
    enable: bool = True
    update_interval: int = 10
    idle_update_interval: int = 400
    minimum_axle_rotation: int = 4
    maximum_rotation_difference_front: float = 0.002
    maximum_rotation_difference_rear: float = 0.002
    wheel_lock_threshold: float = 0.3
    minimum_delta_distance: int = 5
    enable_suspension_measurement_while_offroad: bool = False
    average_suspension_position_samples: int = 20
    average_suspension_position_margin: int = 1
    wheel_lift_off_threshold: int = 1
    cornering_radius_sampling_interval: int = 10


MODULE: Dict[str, FlatMixin] = {
    'module_delta': ModuleDeltaConfig(),
    'module_force': ModuleForceConfig(),
    'module_fuel': ModuleFuelConfig(),
    'module_hybrid': ModuleHybridConfig(),
    'module_mapping': ModuleMappingConfig(),
    'module_notes': ModuleNotesConfig(),
    'module_relative': ModuleRelativeConfig(),
    'module_sectors': ModuleSectorsConfig(),
    'module_stats': ModuleStatsConfig(),
    'module_stint': ModuleStintConfig(),
    'module_vehicles': ModuleVehiclesConfig(),
    'module_wheels': ModuleWheelsConfig(),
}
