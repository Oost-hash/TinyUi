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

"""Write capability for runtime V2 UI panel state."""

from __future__ import annotations

from runtimeV2.ui.panel_state import UIPanelStateStore


class PanelStateWrite:
    """Write runtime-owned UI panel visibility."""

    def __init__(self, store: UIPanelStateStore) -> None:
        self._store = store

    def set_plugin_panel_visible(self, visible: bool) -> bool:
        """Set whether the runtime plugin panel is visible."""

        return self._store.set_plugin_panel_visible(visible)

    def toggle_plugin_panel(self) -> bool:
        """Toggle runtime-owned plugin panel visibility."""

        return self._store.toggle_plugin_panel()
