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

"""Startup for the runtime V2 paths domain."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from runtimeV2.paths.capabilities.path import PathCapability
from runtimeV2.contracts import RuntimePaths
from runtimeV2.paths.detection import detect_runtime_paths
from runtimeV2.paths.startup_shutdown.register_capabilities import register_path_capabilities
from runtimeV2.paths.startup_shutdown.register_paths import register_app_paths
from runtimeV2.runtime import RuntimeV2
from runtimeV2.schemas.startup import StartupResult, startup_error, startup_ok


@dataclass(frozen=True)
class PathsStartupResult:
    """Result of paths domain startup."""

    runtime_paths: RuntimePaths
    named_paths: dict[str, Path]
    capability: PathCapability


def startup_paths(runtime: RuntimeV2) -> StartupResult:
    """Start the paths domain and register its result with runtime."""

    try:
        runtime_paths = detect_runtime_paths()
        named_paths = register_app_paths(runtime_paths)
        capability = register_path_capabilities(
            runtime_paths=runtime_paths,
            named_paths=named_paths,
        )
        result = PathsStartupResult(
            runtime_paths=runtime_paths,
            named_paths=named_paths,
            capability=capability,
        )
        runtime.register_capability("paths", capability)
        runtime.register_domain_result("paths", result)
        return startup_ok()
    except Exception as exc:
        return startup_error(f"Paths domain startup failed: {exc}")

