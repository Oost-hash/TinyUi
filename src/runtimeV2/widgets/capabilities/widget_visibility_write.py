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

"""Widget visibility write capability for runtime V2."""

from __future__ import annotations

from runtimeV2.events.contracts import EventBus, EventType
from runtimeV2.contracts import WidgetConfigWriter
from runtimeV2.widgets.capabilities.widget_manual_override import WidgetManualOverride
from runtimeV2.widgets.contracts import WidgetVisibilityChangedData
from runtimeV2.widgets.visibility_focus import WidgetVisibilityFocus


class WidgetVisibilityWrite:
    """Write widget visibility state owned by the widgets domain."""

    def __init__(
        self,
        widget_config_write: WidgetConfigWriter,
        manual_override: WidgetManualOverride,
        events: EventBus | None = None,
        focus: WidgetVisibilityFocus | None = None,
    ) -> None:
        self._widget_config_write = widget_config_write
        self._manual_override = manual_override
        self._focus = focus
        self._events = events

    def set_global_visible(self, visible: bool) -> None:
        """Set global widget visibility.

        When the user manually enables widgets, we track this so connectors
        cannot override and hide them. The user retains control.
        """

        self._widget_config_write.set_global_widgets_visible(visible)
        # Track manual override: if user explicitly enables widgets, remember this
        if visible:
            self._manual_override.set_manually_enabled(True)
        else:
            self._manual_override.set_manually_enabled(False)
        self._emit_changed(
            WidgetVisibilityChangedData(
                scope="global",
                global_visible=visible,
            )
        )

    def set_global_visible_from_connector(self, visible: bool) -> bool:
        """Set global widget visibility from a connector.

        Connectors can only show widgets (when game is live) but cannot
        hide them if the user has manually enabled widgets.

        Returns True if the visibility was actually changed.
        """

        # If connector wants to hide widgets but user manually enabled them,
        # respect the user's choice and do nothing.
        if not visible and self._manual_override.is_manually_enabled():
            return False

        # Connector is allowed to change visibility
        self._widget_config_write.set_global_widgets_visible(visible)
        # Reset manual override when connector hides widgets (user didn't intervene)
        if not visible:
            self._manual_override.set_manually_enabled(False)
        self._emit_changed(
            WidgetVisibilityChangedData(
                scope="global",
                global_visible=visible,
            )
        )
        return True

    def set_widget_enabled(self, overlay_id: str, widget_id: str, enabled: bool) -> bool:
        """Set one widget enabled state."""

        updated = self._widget_config_write.set_widget_enabled(overlay_id, widget_id, enabled)
        if updated:
            self._emit_changed(
                WidgetVisibilityChangedData(
                    scope="widget",
                    global_visible=True,
                    overlay_id=overlay_id,
                    widget_id=widget_id,
                    enabled=enabled,
                )
            )
        return updated

    def focus_widget(self, overlay_id: str, widget_id: str) -> bool:
        """Focus one widget without changing persisted widget config."""

        if self._focus is None:
            return False
        updated = self._focus.focus_widget(overlay_id, widget_id)
        if updated:
            self._emit_changed(
                WidgetVisibilityChangedData(
                    scope="widget_focus",
                    global_visible=True,
                    overlay_id=overlay_id,
                    widget_id=widget_id,
                )
            )
        return updated

    def clear_focus(self) -> bool:
        """Clear the runtime-only focused widget target."""

        if self._focus is None:
            return False
        focused_widget = self._focus.focused_widget()
        updated = self._focus.clear_focus()
        if updated:
            overlay_id, widget_id = focused_widget if focused_widget is not None else ("", "")
            self._emit_changed(
                WidgetVisibilityChangedData(
                    scope="widget_focus",
                    global_visible=False,
                    overlay_id=overlay_id,
                    widget_id=widget_id,
                )
            )
        return updated

    def _emit_changed(self, data: WidgetVisibilityChangedData) -> None:
        if self._events is None:
            return
        self._events.emit_typed(
            EventType.WIDGET_VISIBILITY_CHANGED,
            data,
            source="widgets",
        )
