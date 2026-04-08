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

"""Runtime V2 startup result contracts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Sequence


@dataclass(frozen=True)
class StartupResult:
    """Minimal result shape for runtime V2 startup steps."""

    ok: bool
    error_message: str = ""


@dataclass(frozen=True)
class StartupStep:
    """One named startup station in the runtime V2 pipeline."""

    name: str
    run: Callable[[], StartupResult]


def startup_ok() -> StartupResult:
    """Return a successful startup result."""

    return StartupResult(ok=True)


def startup_error(error_message: str) -> StartupResult:
    """Return a failed startup result with a user-facing reason."""

    return StartupResult(ok=False, error_message=error_message)


def run_startup_pipeline(steps: Sequence[StartupStep]) -> StartupResult:
    """Run startup steps in order and stop at the first failure."""

    for step in steps:
        result = step.run()
        if not result.ok:
            if result.error_message:
                return result
            return startup_error(f"Startup step failed: {step.name}")
    return startup_ok()
