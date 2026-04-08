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

"""Runtime V2 startup prototype."""

from __future__ import annotations

from dataclasses import dataclass

from runtimeV2.register_capabilities import register_runtime_capabilities
from runtimeV2.register_domains import register_default_domains
from runtimeV2.register_events import register_runtime_events
from runtimeV2.register_globals import register_runtime_globals
from runtimeV2.events.startup import EventsStartupResult
from runtimeV2.plugins.startup import startup_plugins_lifecycle
from runtimeV2.runtime import RuntimeV2
from runtimeV2.schemas.startup import StartupResult, startup_error, startup_ok


@dataclass(frozen=True)
class RuntimeV2StartupResult:
    """Result of runtime V2 startup."""

    runtime: RuntimeV2


_runtime_v2_result: RuntimeV2StartupResult | None = None


def startup_runtime_v2() -> StartupResult:
    """Start the runtime V2 prototype and its first domains."""

    global _runtime_v2_result

    try:
        runtime = RuntimeV2()
        register_runtime_capabilities(runtime)
        register_runtime_globals(runtime)
        register_default_domains(runtime)

        startup_result = runtime.start_domain("events")
        if not startup_result.ok:
            _runtime_v2_result = None
            return startup_result

        events = runtime.domain_result("events", EventsStartupResult)
        register_runtime_events(events.registry)

        for domain_name in runtime.domain_names():
            if domain_name == "events":
                continue
            startup_result = runtime.start_domain(domain_name)
            if not startup_result.ok:
                _runtime_v2_result = None
                return startup_result
            if domain_name == "connectors":
                startup_result = startup_plugins_lifecycle(runtime)
                if not startup_result.ok:
                    _runtime_v2_result = None
                    return startup_result

        _runtime_v2_result = RuntimeV2StartupResult(runtime=runtime)
        return startup_ok()
    except Exception as exc:
        _runtime_v2_result = None
        return startup_error(f"Runtime V2 startup failed: {exc}")


def get_runtime_v2_result() -> RuntimeV2StartupResult | None:
    """Return the last successful runtime V2 startup result."""

    return _runtime_v2_result
