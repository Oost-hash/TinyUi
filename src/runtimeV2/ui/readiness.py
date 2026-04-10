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

"""UI render readiness for runtime V2."""

from __future__ import annotations

from runtimeV2.host.capabilities.main_window_read import MainWindowRead
from runtimeV2.ui.contracts import UIRenderStatus, UIWindowRecord


def determine_render_status(
    *,
    main_window_read: MainWindowRead,
    records: list[UIWindowRecord],
) -> UIRenderStatus:
    """Determine whether the UI host layer has enough data to render."""

    main_window_id = main_window_read.main_window_id()
    main_record = next((record for record in records if record.window_id == main_window_id), None)
    if main_record is None:
        return UIRenderStatus(False, "Main window record is missing", main_window_id)
    if not main_record.surface and not main_record.chrome_surface:
        return UIRenderStatus(False, "Main window render target is missing", main_window_id)
    return UIRenderStatus(True, "", main_window_id)
