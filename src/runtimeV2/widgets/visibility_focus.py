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

"""Runtime-only widget visibility focus state."""

from __future__ import annotations


class WidgetVisibilityFocus:
    """Track the runtime-only focused widget preview target."""

    def __init__(self) -> None:
        self._focused_widget: tuple[str, str] | None = None

    def focused_widget(self) -> tuple[str, str] | None:
        """Return the currently focused widget, if any."""

        return self._focused_widget

    def focus_widget(self, overlay_id: str, widget_id: str) -> bool:
        """Focus one widget for runtime preview visibility."""

        target = (overlay_id, widget_id)
        changed = self._focused_widget != target
        self._focused_widget = target
        return changed

    def clear_focus(self) -> bool:
        """Clear the focused widget target."""

        if self._focused_widget is None:
            return False
        self._focused_widget = None
        return True
