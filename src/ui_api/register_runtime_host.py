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

"""ui_api registration for shared runtime host projections."""

from __future__ import annotations

from shared_runtime_host.register_capabilities import (
    register_ui_actions_host,
    register_ui_host,
    register_window_host,
)
from shared_runtime_host.registry import SharedRuntimeHostRegistry


def register_ui_runtime_host(registry: SharedRuntimeHostRegistry) -> None:
    """Register ui_api-specific host projections when needed."""

    register_ui_host(registry)
    register_window_host(registry)
    register_ui_actions_host(registry)
