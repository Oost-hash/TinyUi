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

"""Widget API host layer above runtime V2."""

from widget_api.runtime_host import (
    WidgetRuntimeHostResult,
    WidgetWindowHostController,
    create_widget_window_host,
    start_widget_host,
)
from widget_api.startup import startup_widget_api
from widget_api.window_host import WidgetWindowHost

__all__ = [
    "WidgetRuntimeHostResult",
    "WidgetWindowHostController",
    "WidgetWindowHost",
    "create_widget_window_host",
    "start_widget_host",
    "startup_widget_api",
]
