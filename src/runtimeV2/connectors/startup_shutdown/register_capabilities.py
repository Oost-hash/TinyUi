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

"""Capability registration for runtime V2 connectors."""

from __future__ import annotations

from dataclasses import dataclass

from runtimeV2.connectors.capabilities.connector_scheduler_write import ConnectorSchedulerWrite
from runtimeV2.events.contracts import EventBus
from runtimeV2.connectors.capabilities.connector_read import ConnectorRead
from runtimeV2.connectors.capabilities.connector_write import ConnectorWrite
from runtimeV2.connectors.poller import ConnectorServicePoller
from runtimeV2.connectors.service_registry import ConnectorServiceRegistry
from runtimeV2.scheduler.capabilities.scheduler_write import SchedulerWrite


@dataclass(frozen=True)
class ConnectorCapabilities:
    """Capabilities exposed by the connectors domain."""

    read: ConnectorRead
    write: ConnectorWrite
    scheduler_write: ConnectorSchedulerWrite


def register_connector_capabilities(
    registry: ConnectorServiceRegistry,
    poller: ConnectorServicePoller,
    scheduler_write: SchedulerWrite,
    live_interval_ms: int,
    events: EventBus | None = None,
) -> ConnectorCapabilities:
    """Create connector domain capabilities."""

    return ConnectorCapabilities(
        read=ConnectorRead(registry),
        write=ConnectorWrite(registry, poller, events),
        scheduler_write=ConnectorSchedulerWrite(
            ConnectorRead(registry),
            scheduler_write,
            poller,
            live_interval_ms=live_interval_ms,
        ),
    )
