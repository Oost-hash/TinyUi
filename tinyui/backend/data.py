"""
Auto-generated adapter file. Do not edit manually.
Generated from manifest.json - update there instead.
"""


from tinypedal.userfile import (
    set_relative_path,
    set_user_data_path,
)

from tinypedal.userfile.consumption_history import load_consumption_history_file

from tinypedal.userfile.driver_stats import (
    DriverStats,
    load_stats_json_file,
    save_stats_json_file,
    validate_stats_file,
)

from tinypedal.userfile.heatmap import (
    HEATMAP_DEFAULT_BRAKE,
    HEATMAP_DEFAULT_TYRE,
    set_predefined_brake_name,
    set_predefined_compound_symbol,
)

from tinypedal.userfile.track_map import load_track_map_file

from tinypedal.userfile.track_notes import (
    COLUMN_PACENOTE,
    NOTESTYPE_PACE,
    NOTESTYPE_TRACK,
    create_notes_metadata,
    load_notes_file,
    save_notes_file,
    set_notes_filter,
    set_notes_header,
    set_notes_parser,
    set_notes_writer,
)

from tinypedal.template.setting_shortcuts import (
    SHORTCUTS_GENERAL,
    SHORTCUTS_MODULE,
    SHORTCUTS_WIDGET,
)

from tinypedal.template.setting_tracks import TRACKINFO_DEFAULT
