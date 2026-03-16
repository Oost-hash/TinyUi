# Auto-generated api configuration

from dataclasses import dataclass
from typing import Any, Dict

from .base import FlatMixin


@dataclass
class ApiLmuConfigConfig(FlatMixin):
    access_mode: int = 0
    enable_active_state_override: bool = False
    active_state: bool = True
    enable_player_index_override: bool = False
    player_index: int = -1
    character_encoding: str = 'UTF-8'
    enable_restapi_access: bool = True
    restapi_update_interval: int = 200
    url_host: str = 'localhost'
    url_port: int = 6397
    connection_timeout: int = 1
    connection_retry: int = 3
    connection_retry_delay: int = 1
    enable_energy_remaining: bool = True
    enable_garage_setup_info: bool = True
    enable_session_info: bool = True
    enable_vehicle_info: bool = True
    enable_weather_info: bool = True


@dataclass
class ApiRf2ConfigConfig(FlatMixin):
    access_mode: int = 0
    process_id: str = ''
    enable_active_state_override: bool = False
    active_state: bool = True
    enable_player_index_override: bool = False
    player_index: int = -1
    character_encoding: str = 'UTF-8'
    enable_restapi_access: bool = True
    restapi_update_interval: int = 200
    url_host: str = 'localhost'
    url_port: int = 5397
    connection_timeout: int = 1
    connection_retry: int = 3
    connection_retry_delay: int = 1
    enable_garage_setup_info: bool = True
    enable_session_info: bool = True
    enable_weather_info: bool = True


API: Dict[str, FlatMixin] = {
    'API_LMU_CONFIG': ApiLmuConfigConfig(),
    'API_RF2_CONFIG': ApiRf2ConfigConfig(),
}
