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

"""Runtime global state capability."""

from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

from runtimeV2.contracts import EventType
from runtimeV2.globals import GlobalRegistration

if TYPE_CHECKING:
    from runtimeV2.runtime import RuntimeV2

T = TypeVar("T")


class RuntimeGlobals:
    """Register and resolve runtime-visible cross-domain global states."""

    def __init__(self, runtime: RuntimeV2) -> None:
        self._runtime = runtime

    def register_global(
        self,
        name: str,
        *,
        owner_domain: str,
        description: str = "",
        read_capability: str = "",
        write_capability: str = "",
        event_type: EventType | None = None,
    ) -> None:
        """Register a runtime-visible cross-domain global state."""

        self._runtime.register_global(
            name,
            owner_domain=owner_domain,
            description=description,
            read_capability=read_capability,
            write_capability=write_capability,
            event_type=event_type,
        )

    def read_global(self, name: str, capability_type: type[T]) -> T:
        """Return the read capability for a registered global state."""

        registration = self._runtime.global_record(name)
        if not registration.read_capability:
            raise KeyError(f"Runtime V2 global state has no read capability: {name}")
        return self._runtime.capability(registration.read_capability, capability_type)

    def write_global(self, name: str, capability_type: type[T]) -> T:
        """Return the write capability for a registered global state."""

        registration = self._runtime.global_record(name)
        if not registration.write_capability:
            raise KeyError(f"Runtime V2 global state has no write capability: {name}")
        return self._runtime.capability(registration.write_capability, capability_type)

    def global_records(self) -> list[GlobalRegistration]:
        """Return registered cross-domain global states."""

        return self._runtime.global_records()

    def global_record(self, name: str) -> GlobalRegistration:
        """Return one registered cross-domain global state."""

        return self._runtime.global_record(name)
