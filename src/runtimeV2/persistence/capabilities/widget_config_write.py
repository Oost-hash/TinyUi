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

"""Widget config write capability."""

from __future__ import annotations

from runtimeV2.persistence.widget_config import WidgetConfigStore


class WidgetConfigWrite:
    """Write widget config values."""

    def __init__(self, store: WidgetConfigStore) -> None:
        self._store = store

    def set_widget_enabled(self, overlay_id: str, widget_id: str, enabled: bool) -> bool:
        """Set widget enabled state."""

        return self._store.set_widget_enabled(overlay_id, widget_id, enabled)

    def set_widget_position(self, overlay_id: str, widget_id: str, x: int, y: int) -> bool:
        """Set widget position."""

        return self._store.set_widget_position(overlay_id, widget_id, x, y)

    def set_widget_values(self, overlay_id: str, widget_id: str, values: dict[str, object]) -> bool:
        """Set widget config values."""

        return self._store.set_widget_values(overlay_id, widget_id, values)

    def reset_widget_values(self, overlay_id: str, widget_id: str) -> bool:
        """Reset widget config values."""

        return self._store.reset_widget_values(overlay_id, widget_id)

    def set_global_widgets_visible(self, visible: bool) -> None:
        """Set global widget visibility."""

        self._store.set_global_visible(visible)
