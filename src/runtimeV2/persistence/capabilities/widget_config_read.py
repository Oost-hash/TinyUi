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

"""Widget config read capability."""

from __future__ import annotations

from runtimeV2.persistence.contracts import WidgetInstanceConfig
from runtimeV2.persistence.widget_config import WidgetConfigStore


class WidgetConfigRead:
    """Read widget config values."""

    def __init__(self, store: WidgetConfigStore) -> None:
        self._store = store

    def get_overlay(self, overlay_id: str) -> list[WidgetInstanceConfig]:
        """Return config for one overlay."""

        return self._store.load_for_overlay(overlay_id)

    def get_widget(self, overlay_id: str, widget_id: str) -> WidgetInstanceConfig | None:
        """Return config for one widget."""

        return self._store.get_widget(overlay_id, widget_id)

    def widget_values(self, overlay_id: str, widget_id: str) -> dict[str, object]:
        """Return config values for one widget."""

        widget = self._store.get_widget(overlay_id, widget_id)
        return dict(widget.values) if widget is not None else {}

    def global_widgets_visible(self) -> bool:
        """Return global widget visibility."""

        return self._store.get_global_visible()
