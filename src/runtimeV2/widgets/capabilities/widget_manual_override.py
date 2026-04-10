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

"""Widget manual override capability for runtime V2."""

from __future__ import annotations


class WidgetManualOverride:
    """Track whether the user has manually toggled widget visibility.

    When the user manually enables widgets, connectors should not be able
    to hide them. Only when a game is actively running can the connector
    override and show widgets (but never hide them if user wants them on).
    """

    def __init__(self) -> None:
        self._manually_enabled = False

    def is_manually_enabled(self) -> bool:
        """Return True if the user has manually enabled widgets."""

        return self._manually_enabled

    def set_manually_enabled(self, enabled: bool) -> None:
        """Set whether the user has manually enabled widgets."""

        self._manually_enabled = enabled

    def can_connector_hide_widgets(self) -> bool:
        """Return True if the connector is allowed to hide widgets.

        When the user has manually enabled widgets, the connector cannot
        hide them. The connector can only show widgets (when game is live).
        """

        return not self._manually_enabled
