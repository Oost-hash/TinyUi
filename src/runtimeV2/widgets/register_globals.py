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

"""Global state registration for runtime V2 widgets."""

from __future__ import annotations

from runtimeV2.runtime import RuntimeV2


def register_widget_globals(runtime: RuntimeV2) -> None:
    """Register widget-owned cross-domain global states."""

    runtime.register_global(
        "widget_visibility",
        owner_domain="widgets",
        read_capability="widget_visibility_read",
        write_capability="widget_visibility_write",
        description="Global widget visibility state.",
    )
