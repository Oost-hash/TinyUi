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

"""Public event contracts used outside the events domain."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from runtimeV2.events.contracts import EventCallback, EventType


@runtime_checkable
class EventSubscriptionHandle(Protocol):
    """Public contract for closing one runtime event subscription."""

    def close(self) -> None:
        """Release one runtime event subscription."""
        ...


@runtime_checkable
class EventRegistrationWriter(Protocol):
    """Public contract for runtime event registration and subscriptions."""

    def register_event(
        self,
        owner_domain: str,
        event_type: EventType,
        description: str = "",
    ) -> None:
        """Register one runtime event contract."""
        ...

    def subscribe(
        self,
        owner_domain: str,
        event_type: EventType,
        callback: EventCallback,
        *,
        replay_history: bool = False,
        description: str = "",
    ) -> EventSubscriptionHandle:
        """Subscribe one callback to a runtime event."""
        ...
