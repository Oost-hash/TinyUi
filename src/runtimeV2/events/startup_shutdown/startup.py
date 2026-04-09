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

"""Startup for the runtime V2 events domain."""

from __future__ import annotations

from dataclasses import dataclass

from runtimeV2.events.contracts import EventBus
from runtimeV2.events.capabilities.event_read import EventRead
from runtimeV2.events.event_registry import EventRegistry
from runtimeV2.events.startup_shutdown.register_capabilities import register_event_capabilities
from runtimeV2.events.startup_shutdown.register_events import register_events_domain_events
from runtimeV2.runtime import RuntimeV2
from runtimeV2.schemas.startup import StartupResult, startup_error, startup_ok


@dataclass(frozen=True)
class EventsStartupResult:
    """Result of events domain startup."""

    bus: EventBus
    registry: EventRegistry
    event_read: EventRead


def startup_events(runtime: RuntimeV2) -> StartupResult:
    """Start the events domain and register its result with runtime."""

    try:
        bus = EventBus()
        registry = EventRegistry()
        register_events_domain_events(registry)
        event_read = register_event_capabilities(registry)
        result = EventsStartupResult(bus=bus, registry=registry, event_read=event_read)
        runtime.register_capability("event_read", event_read)
        runtime.register_domain_result("events", result)
        return startup_ok()
    except Exception as exc:
        return startup_error(f"Events domain startup failed: {exc}")

