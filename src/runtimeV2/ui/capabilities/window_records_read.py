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

"""Window records read capability for runtime V2 UI."""

from __future__ import annotations

from runtimeV2.contracts import UIWindowRecord


class WindowRecordsRead:
    """Read runtime V2 UI window records."""

    def __init__(self, records: list[UIWindowRecord]) -> None:
        self._records = records

    def all_window_records(self) -> list[UIWindowRecord]:
        """Return all window records."""

        return list(self._records)

    def window_record(self, window_id: str) -> UIWindowRecord | None:
        """Return one window record."""

        return next((record for record in self._records if record.window_id == window_id), None)
