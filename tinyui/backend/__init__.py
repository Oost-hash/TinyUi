"""TinyPedal backend adapter layer."""

from .config_adapter import ConfigAdapter
from .lazy import LazyModule
from .settings import (
    copy_setting,
    load_setting_json_file,
    save_and_verify_json_file,
)

config = ConfigAdapter()


def init_backend(real_cfg):
    config.inject_real(real_cfg)


# Lazy proxies voor TinyPedal modules
api = LazyModule("tinypedal_repo.tinypedal.api_control", "api")
loader = LazyModule("tinypedal_repo.tinypedal.loader")
kctrl = LazyModule("tinypedal_repo.tinypedal.hotkey_control", "kctrl")
mctrl = LazyModule("tinypedal_repo.tinypedal.module_control", "mctrl")
octrl = LazyModule("tinypedal_repo.tinypedal.overlay_control", "octrl")
wctrl = LazyModule("tinypedal_repo.tinypedal.module_control", "wctrl")
update_checker = LazyModule("tinypedal_repo.tinypedal.update", "update_checker")
minfo = LazyModule("tinypedal_repo.tinypedal.module_info", "minfo")
calc = LazyModule("tinypedal_repo.tinypedal.calculation")
units = LazyModule("tinypedal_repo.tinypedal.units")
realtime_state = LazyModule("tinypedal_repo.tinypedal.realtime_state")

# Exporteer ook de minimale gegenereerde modules
from .constants import *
from .misc import *
