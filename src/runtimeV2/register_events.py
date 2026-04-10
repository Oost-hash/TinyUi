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

"""Runtime V2 event contract registration."""

from __future__ import annotations

from runtimeV2.events.contracts import EventType
from runtimeV2.events.event_registry import EventRegistry


def register_runtime_events(registry: EventRegistry) -> None:
    """Register runtime-owned domain status events."""

    registry.register(
        EventType.DOMAIN_REGISTERED,
        domain="runtime",
        description="A runtime V2 domain was registered.",
    )
    registry.register(
        EventType.DOMAIN_STARTING,
        domain="runtime",
        description="Runtime V2 is starting a domain.",
    )
    registry.register(
        EventType.DOMAIN_READY,
        domain="runtime",
        description="A runtime V2 domain finished startup.",
    )
    registry.register(
        EventType.DOMAIN_ERROR,
        domain="runtime",
        description="A runtime V2 domain failed startup.",
    )
    registry.register(
        EventType.DOMAIN_STOPPED,
        domain="runtime",
        description="A runtime V2 domain stopped.",
    )
    registry.register(
        EventType.RUNTIME_SHUTDOWN,
        domain="runtime",
        description="Runtime shutdown was requested.",
    )
