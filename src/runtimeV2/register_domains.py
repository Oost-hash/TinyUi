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

"""Runtime V2 domain registration."""

from __future__ import annotations

from runtimeV2.events.startup import startup_events
from runtimeV2.paths.startup import startup_paths
from runtimeV2.runtime import RuntimeV2


def register_default_domains(runtime: RuntimeV2) -> None:
    """Register the first runtime V2 domains in startup order."""

    runtime.register_domain(
        "events",
        startup_events,
        description="Owns the eventbus and event registry.",
    )
    runtime.register_domain(
        "paths",
        startup_paths,
        description="Owns one-time path detection and path access.",
    )
