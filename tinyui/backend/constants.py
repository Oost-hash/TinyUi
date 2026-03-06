"""
Re-export TinyPedal constants used by TinyUi.

Single source for all constant imports — if TinyPedal renames or
reorganizes, only this file needs updating.
"""

# --- const_app ---
from tinypedal.const_app import (
    APP_NAME as TP_APP_NAME,
    COPYRIGHT as TP_COPYRIGHT,
    DESCRIPTION as TP_DESCRIPTION,
    LICENSE as TP_LICENSE,
    PLATFORM,
    VERSION as TP_VERSION,
    URL_FAQ,
    URL_RELEASE,
    URL_USER_GUIDE,
    URL_WEBSITE,
)

# --- const_file ---
from tinypedal.const_file import (
    ConfigType,
    FileExt,
    FileFilter,
    ImageFile,
)

# --- const_common (only what tinyui uses) ---
from tinypedal.const_common import (
    EMPTY_DICT,
    MAX_SECONDS,
    TEXT_NOLAPTIME,
)

# --- const_api (only what tinyui uses) ---
from tinypedal.const_api import (
    API_LMU_ALIAS,
    API_LMU_CONFIG,
    API_RF2_ALIAS,
    API_RF2_CONFIG,
)
