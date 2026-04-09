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

"""Domain contracts for the runtime V2 orchestrator."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING, Callable

from runtimeV2.schemas.startup import StartupResult

if TYPE_CHECKING:
    from runtimeV2.runtime import RuntimeV2


class DomainStatus(StrEnum):
    """Observable startup status for one runtime V2 domain."""

    REGISTERED = "registered"
    STARTING = "starting"
    READY = "ready"
    ERROR = "error"
    STOPPED = "stopped"


DomainStartup = Callable[["RuntimeV2"], StartupResult]

@dataclass(frozen=True)
class DomainRegistration:
    """A registered runtime V2 domain."""

    name: str
    startup: DomainStartup
    description: str = ""


@dataclass(frozen=True)
class DomainRecord:
    """Runtime-owned observable record for one domain."""

    name: str
    description: str
    status: DomainStatus
    error_message: str = ""
