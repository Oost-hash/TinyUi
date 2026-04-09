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

"""UI-owned panel state for runtime V2."""

from __future__ import annotations

from runtimeV2.events.contracts import EventType
from runtimeV2.events.startup import EventsStartupResult
from runtimeV2.ui.contracts import UIPanelVisibilityChangedData


class UIPanelStateStore:
    """Store runtime-owned UI panel visibility."""

    def __init__(self, events: EventsStartupResult) -> None:
        self._events = events
        self._plugin_panel_visible = False

    def plugin_panel_visible(self) -> bool:
        """Return whether the runtime plugin panel is visible."""

        return self._plugin_panel_visible

    def set_plugin_panel_visible(self, visible: bool) -> bool:
        """Set runtime-owned plugin panel visibility."""

        if self._plugin_panel_visible == visible:
            return False
        self._plugin_panel_visible = visible
        self._events.bus.emit_typed(
            EventType.UI_PANEL_VISIBILITY_CHANGED,
            UIPanelVisibilityChangedData(visible=visible),
            source="ui",
        )
        return True

    def toggle_plugin_panel(self) -> bool:
        """Toggle runtime-owned plugin panel visibility."""

        return self.set_plugin_panel_visible(not self._plugin_panel_visible)
