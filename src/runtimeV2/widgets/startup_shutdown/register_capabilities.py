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
from runtimeV2.scheduler.capabilities.scheduler_clock_read import SchedulerClockRead
from runtimeV2.scheduler.capabilities.scheduler_write import SchedulerWrite
from runtimeV2.widgets.capabilities.widget_manual_override import WidgetManualOverride
from runtimeV2.widgets.capabilities.widget_records_read import WidgetRecordsRead
from runtimeV2.widgets.capabilities.widget_records_refresh import WidgetRecordsRefresh
from runtimeV2.widgets.capabilities.widget_refresh_policy import WidgetRefreshPolicy
from runtimeV2.widgets.capabilities.widget_visibility_read import WidgetVisibilityRead
from runtimeV2.widgets.capabilities.widget_visibility_write import WidgetVisibilityWrite
from runtimeV2.widgets.store import WidgetRecordsStore


@dataclass(frozen=True)
class WidgetCapabilities:
    """Widgets domain capabilities."""

    records_read: WidgetRecordsRead
    records_refresh: WidgetRecordsRefresh
    refresh_policy: WidgetRefreshPolicy
    visibility_read: WidgetVisibilityRead
    visibility_write: WidgetVisibilityWrite
    manual_override: WidgetManualOverride


def register_widget_capabilities(
    *,
    store: WidgetRecordsStore,
    overlay_read,
    connector_decl_read,
    connector_read,
    active_read,
    widget_config_read: WidgetConfigRead,
    widget_config_write: WidgetConfigWrite,
    scheduler_write: SchedulerWrite,
    scheduler_clock_read: SchedulerClockRead,
    events: EventBus,
) -> WidgetCapabilities:
    """Create widgets domain capabilities."""

    records_refresh = WidgetRecordsRefresh(
        store=store,
        overlay_read=overlay_read,
        connector_decl_read=connector_decl_read,
        connector_read=connector_read,
        active_read=active_read,
        widget_config_read=widget_config_read,
        events=events,
    )
    visibility_read = WidgetVisibilityRead(widget_config_read)
    manual_override = WidgetManualOverride()
    return WidgetCapabilities(
        records_read=WidgetRecordsRead(store),
        records_refresh=records_refresh,
        refresh_policy=WidgetRefreshPolicy(
            records_refresh=records_refresh,
            visibility_read=visibility_read,
            scheduler_write=scheduler_write,
            scheduler_clock_read=scheduler_clock_read,
            events=events,
        ),
        visibility_read=visibility_read,
        visibility_write=WidgetVisibilityWrite(
            widget_config_write=widget_config_write,
            manual_override=manual_override,
            events=events,
        ),
        manual_override=manual_override,
    )
