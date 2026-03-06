"""
Re-export TinyPedal setting objects used by TinyUi.

Single source for all setting imports — if TinyPedal renames or
reorganizes, only this file needs updating.
"""

from tinypedal.setting import (
    cfg,
    copy_setting,
    load_setting_json_file,
    save_and_verify_json_file,
)
