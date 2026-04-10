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

"""Render status read capability for runtime V2 UI."""

from __future__ import annotations

from runtimeV2.contracts import UIRenderStatus


class RenderStatusRead:
    """Read UI render readiness."""

    def __init__(self, status: UIRenderStatus) -> None:
        self._status = status

    def is_render_ready(self) -> bool:
        """Return True when UI can render."""

        return self._status.render_ready

    def render_blocker(self) -> str:
        """Return the render blocker when UI cannot render."""

        return self._status.render_blocker

    def main_window_id(self) -> str:
        """Return the host main window id."""

        return self._status.main_window_id
