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

"""Public widget contracts used outside the widgets domain."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from runtimeV2.widgets.contracts import WidgetRecord, WidgetVisibilityState


@runtime_checkable
class WidgetRecordsReader(Protocol):
    """Public contract for reading projected widget records."""

    def all_widget_records(self) -> list[WidgetRecord]:
        """Return all widget records."""
        ...

    def records_for_overlay(self, overlay_id: str) -> list[WidgetRecord]:
        """Return widget records for one overlay."""
        ...

    def widget_record(self, overlay_id: str, widget_id: str) -> WidgetRecord | None:
        """Return one widget runtime record."""
        ...


@runtime_checkable
class WidgetVisibilityReader(Protocol):
    """Public contract for reading widget visibility outside the widgets domain."""

    def state(self) -> WidgetVisibilityState:
        """Return widget visibility state."""
        ...

    def global_visible(self) -> bool:
        """Return global widget visibility."""
        ...

    def is_widget_enabled(self, overlay_id: str, widget_id: str) -> bool:
        """Return whether one widget is enabled."""
        ...


@runtime_checkable
class WidgetVisibilityWriter(Protocol):
    """Public contract for mutating widget visibility outside the widgets domain."""

    def set_global_visible(self, visible: bool) -> None:
        """Set global widget visibility from user-facing callers."""
        ...

    def set_global_visible_from_connector(self, visible: bool) -> bool:
        """Set global widget visibility from connector policy."""
        ...

    def set_widget_enabled(self, overlay_id: str, widget_id: str, enabled: bool) -> bool:
        """Set one widget enabled state."""
        ...


@runtime_checkable
class WidgetManualOverrideState(Protocol):
    """Public contract for widget manual override state."""

    def is_manually_enabled(self) -> bool:
        """Return whether the user manually enabled widgets."""
        ...

    def set_manually_enabled(self, enabled: bool) -> None:
        """Set whether the user manually enabled widgets."""
        ...

    def can_connector_hide_widgets(self) -> bool:
        """Return whether connectors can hide widgets."""
        ...
