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

"""Read capability for runtime V2 UI panel state."""

from __future__ import annotations

from runtimeV2.ui.panel_state import UIPanelStateStore


class PanelStateRead:
    """Read runtime-owned UI panel visibility."""

    def __init__(self, store: UIPanelStateStore) -> None:
        self._store = store

    def plugin_panel_visible(self) -> bool:
        """Return whether the runtime plugin panel is visible."""

        return self._store.plugin_panel_visible()
