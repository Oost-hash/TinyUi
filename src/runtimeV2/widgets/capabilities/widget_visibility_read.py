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

"""Widget visibility read capability for runtime V2."""

from __future__ import annotations

from runtimeV2.persistence.capabilities.widget_config_read import WidgetConfigRead
from runtimeV2.widgets.contracts import WidgetVisibilityState


class WidgetVisibilityRead:
    """Read widget visibility state owned by the widgets domain."""

    def __init__(self, widget_config_read: WidgetConfigRead) -> None:
        self._widget_config_read = widget_config_read

    def state(self) -> WidgetVisibilityState:
        """Return widget visibility state."""

        return WidgetVisibilityState(global_visible=self.global_visible())

    def global_visible(self) -> bool:
        """Return global widget visibility."""

        return self._widget_config_read.global_widgets_visible()

    def is_widget_enabled(self, overlay_id: str, widget_id: str) -> bool:
        """Return True when one widget is enabled."""

        config = self._widget_config_read.get_widget(overlay_id, widget_id)
        return True if config is None else config.enabled
