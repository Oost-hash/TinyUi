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

"""Shared host-facing projection for runtime V2 window records."""

from __future__ import annotations

from runtimeV2.contracts.ui import WindowRecordsReader
from runtimeV2.ui.contracts import UIWindowRecord


class WindowHostCapability:
    """Project UI window records into host-facing shapes."""

    def __init__(self, window_records_read: WindowRecordsReader) -> None:
        self._window_records_read = window_records_read

    def windows(self) -> list[dict[str, object]]:
        """Return all host-facing window records."""

        return [self.window(record) for record in self._window_records_read.all_window_records()]

    def window(self, record: UIWindowRecord) -> dict[str, object]:
        """Return one host-facing window record."""

        return {
            "windowId": record.window_id,
            "pluginId": record.plugin_id,
            "windowRole": record.window_role,
            "status": record.status.value,
            "visible": record.visible,
            "surface": record.surface,
            "chromeSurface": record.chrome_surface,
            "errorMessage": record.error_message,
        }
