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

"""Event contract registration for the runtime V2 events domain."""

from __future__ import annotations

from runtimeV2.contracts import EventType
from runtimeV2.events.event_registry import EventRegistry


def register_events_domain_events(registry: EventRegistry) -> None:
    """Register events-domain event contracts."""

    registry.register(
        EventType.EVENT_REGISTRY_UPDATED,
        domain="events",
        description="The event registry changed.",
    )
