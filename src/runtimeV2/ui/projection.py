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

"""UI window projection for runtime V2."""

from __future__ import annotations

from runtimeV2.host.capabilities.main_window_read import MainWindowRead
from runtimeV2.plugins.capabilities.ui_manifest_read import PluginUiManifestRead
from runtimeV2.ui.contracts import UIWindowRecord, UIWindowStatus


def _window_render_target(window_role: str, surface: str, chrome_surface: str) -> str:
    if surface:
        return surface
    if window_role == "main":
        return chrome_surface
    return ""


def project_ui_window_records(
    *,
    ui_manifest_read: PluginUiManifestRead,
    main_window_read: MainWindowRead,
) -> list[UIWindowRecord]:
    """Project plugin-declared windows into runtime V2 UI records."""

    main_window_id = main_window_read.main_window_id()
    records: list[UIWindowRecord] = []
    for plugin_id, windows in ui_manifest_read.windows().items():
        for window in windows:
            window_role = "main" if window.id == main_window_id else "window"
            surface = "" if window.surface is None else str(window.surface)
            chrome_surface = "" if window.chrome.custom_chrome is None else str(window.chrome.custom_chrome)
            render_target = _window_render_target(window_role, surface, chrome_surface)
            records.append(UIWindowRecord(
                window_id=window.id,
                plugin_id=plugin_id,
                window_role=window_role,
                status=UIWindowStatus.READY if render_target else UIWindowStatus.ERROR,
                visible=window.id == main_window_id,
                surface=surface,
                chrome_surface=chrome_surface,
                error_message="" if render_target else "Window has no render target",
            ))
    return records
