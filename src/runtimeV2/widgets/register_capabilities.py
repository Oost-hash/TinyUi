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

"""Capability registration for runtime V2 widgets."""

from __future__ import annotations

from dataclasses import dataclass

from runtimeV2.events.contracts import EventBus
from runtimeV2.persistence.capabilities.widget_config_read import WidgetConfigRead
from runtimeV2.persistence.capabilities.widget_config_write import WidgetConfigWrite
from runtimeV2.widgets.capabilities.widget_records_read import WidgetRecordsRead
from runtimeV2.widgets.capabilities.widget_visibility_read import WidgetVisibilityRead
from runtimeV2.widgets.capabilities.widget_visibility_write import WidgetVisibilityWrite
from runtimeV2.widgets.store import WidgetRecordsStore


@dataclass(frozen=True)
class WidgetCapabilities:
    """Widgets domain capabilities."""

    records_read: WidgetRecordsRead
    visibility_read: WidgetVisibilityRead
    visibility_write: WidgetVisibilityWrite


def register_widget_capabilities(
    *,
    store: WidgetRecordsStore,
    widget_config_read: WidgetConfigRead,
    widget_config_write: WidgetConfigWrite,
    events: EventBus | None = None,
) -> WidgetCapabilities:
    """Create widgets domain capabilities."""

    return WidgetCapabilities(
        records_read=WidgetRecordsRead(store),
        visibility_read=WidgetVisibilityRead(widget_config_read),
        visibility_write=WidgetVisibilityWrite(widget_config_write, events),
    )
