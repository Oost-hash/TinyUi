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

"""Event registration for runtime V2 scheduler."""

from __future__ import annotations

from runtimeV2.events.contracts import EventType
from runtimeV2.events.event_registry import EventRegistry


def register_scheduler_events(registry: EventRegistry) -> None:
    """Register scheduler domain event contracts."""

    registry.register(
        EventType.SCHEDULER_JOB_REGISTERED,
        domain="scheduler",
        description="A recurring scheduler job was registered.",
    )
    registry.register(
        EventType.SCHEDULER_JOB_UPDATED,
        domain="scheduler",
        description="A recurring scheduler job changed cadence or enabled-state.",
    )
    registry.register(
        EventType.SCHEDULER_CLOCK_UPDATED,
        domain="scheduler",
        description="The central scheduler clock changed mode, cadence, or lock owner.",
    )
    registry.register(
        EventType.SCHEDULER_TICK,
        domain="scheduler",
        description="The scheduler processed one runtime tick.",
    )
