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

"""Window action capability for runtime V2 UI."""

from __future__ import annotations

from runtimeV2.ui.capabilities.window_records_read import WindowRecordsRead


class WindowActionsWrite:
    """Validate and expose runtime-owned UI window actions."""

    def __init__(self, window_records_read: WindowRecordsRead, main_window_id: str) -> None:
        self._window_records_read = window_records_read
        self._main_window_id = main_window_id

    def main_window_id(self) -> str:
        """Return the runtime-owned main window id."""

        return self._main_window_id

    def openable_window_ids(self) -> list[str]:
        """Return non-main window ids that the host may open."""

        return [
            record.window_id
            for record in self._window_records_read.all_window_records()
            if record.window_id != self._main_window_id
        ]

    def can_open_window(self, window_id: str) -> bool:
        """Return whether one window id is openable through the host."""

        return window_id in self.openable_window_ids()

    def request_open_window(self, window_id: str) -> bool:
        """Validate an open-window action request."""

        return self.can_open_window(window_id)
