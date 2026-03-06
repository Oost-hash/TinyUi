"""
Auto-generated adapter file. Do not edit manually.
Generated from manifest.json - update there instead.
"""


from tinypedal import (
    calculation as calc,
    realtime_state,
    units,
)

from tinypedal.async_request import (
    get_response,
    set_header_get,
)

from tinypedal.hotkey.common import (
    format_hotkey_name,
    get_key_state_function,
    refresh_keystate,
    set_hotkey_win,
)

from tinypedal.log_handler import set_logging_level

from tinypedal.main import (
    log_stream,
    set_environment,
    unset_environment,
)

from tinypedal.module_info import (
    ConsumptionDataSet,
    minfo,
)

from tinypedal.update import update_checker
