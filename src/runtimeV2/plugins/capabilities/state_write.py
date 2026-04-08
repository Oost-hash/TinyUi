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

"""Plugin state write capability for runtime V2."""

from __future__ import annotations

from runtimeV2.plugins.lifecycle import PluginLifecycleStore


class PluginStateWrite:
    """Request plugin lifecycle state changes."""

    def __init__(self, lifecycle: PluginLifecycleStore) -> None:
        self._lifecycle = lifecycle

    def enable_plugin(self, plugin_id: str) -> bool:
        """Enable one plugin."""

        return self._lifecycle.enable_plugin(plugin_id)

    def disable_plugin(self, plugin_id: str) -> bool:
        """Disable one plugin."""

        return self._lifecycle.disable_plugin(plugin_id)
