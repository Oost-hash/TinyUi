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

"""Startup helpers for runtime-owned widget state."""

from __future__ import annotations

from typing import Protocol

from runtime_schema import StartupResult, startup_error, startup_ok


class RuntimeWidgetsStartupLike(Protocol):
    """Minimal runtime surface needed to start runtime/widgets."""

    def active_overlay_widget_records(self) -> object: ...


def start_runtime_widgets(runtime: RuntimeWidgetsStartupLike) -> StartupResult:
    """Initialize runtime/widgets readiness before widget hosting begins."""

    try:
        runtime.active_overlay_widget_records()
    except Exception as exc:
        return startup_error(f"runtime/widgets startup failed: {exc}")
    return startup_ok()
