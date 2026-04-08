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

"""Widget API foundation layer."""

from widget_api.contracts import WidgetDefinition
from widget_api.defaults import DEFAULT_WIDGET_DEFINITIONS, create_default_widget_registry
from widget_api.registry import WidgetRegistry
from widget_api.runtime_host import (
    WidgetRuntimeHostResult,
    WidgetWindowHostController,
    create_widget_window_host,
    start_widget_host,
)
from widget_api.startup import startup_widget_api, get_widget_api_result, WidgetApiStartupResult
from widget_api.runtime_adapters import WidgetConfigWriteAdapter, widget_data_for_record
from widget_api.window_host import WidgetWindowHost

__all__ = [
    "DEFAULT_WIDGET_DEFINITIONS",
    "WidgetDefinition",
    "WidgetConfigWriteAdapter",
    "WidgetRegistry",
    "WidgetRuntimeHostResult",
    "WidgetWindowHostController",
    "WidgetWindowHost",
    "create_default_widget_registry",
    "create_widget_window_host",
    "get_widget_api_result",
    "start_widget_host",
    "startup_widget_api",
    "widget_data_for_record",
]
