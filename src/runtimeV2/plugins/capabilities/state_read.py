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

"""Plugin state read capability for runtime V2."""

from __future__ import annotations

from runtime_schema import PluginState
from runtimeV2.plugins.lifecycle import PluginLifecycleStore


class PluginStateRead:
    """Read plugin lifecycle state."""

    def __init__(self, lifecycle: PluginLifecycleStore) -> None:
        self._lifecycle = lifecycle

    def get_plugin_state(self, plugin_id: str) -> PluginState:
        """Return one plugin lifecycle state."""

        return self._lifecycle.get_plugin_state(plugin_id)
