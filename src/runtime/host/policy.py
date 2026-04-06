#  TinyUI
#  Copyright (C) 2026 Oost-hash
#
#  This file is part of TinyUI.
#
#  TinyUI is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  TinyUI is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#  TinyUI builds on TinyPedal by s-victor (https://github.com/s-victor/TinyPedal),
#  licensed under GPLv3.

"""Host-specific runtime policy."""

from __future__ import annotations

from app_schema.plugin import PluginManifest
from app_schema.ui import AppManifest


def active_host_ids(plugins: dict[str, PluginManifest]) -> set[str]:
    """Return host plugin ids that form the baseline runtime shell."""
    return {
        plugin_id
        for plugin_id, manifest in plugins.items()
        if manifest.plugin_type == "host"
    }


def main_window_for(plugins: dict[str, PluginManifest]) -> AppManifest | None:
    """Return the primary host window when available."""
    for manifest in plugins.values():
        if manifest.plugin_type == "host" and manifest.ui and manifest.ui.windows:
            return manifest.ui.windows[0]
    return None
