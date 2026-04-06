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

"""Runtime-owned widget record projection."""

from runtime.widgets.contracts import WidgetRuntimeRecord, WidgetRuntimeStatus
from runtime.widgets.game_detection import detect_active_game_id
from runtime.widgets.poller import WidgetRuntimePoller
from runtime.widgets.projection import project_overlay_widget_records
from runtime.widgets.startup import start_runtime_widgets

__all__ = [
    "detect_active_game_id",
    "WidgetRuntimeRecord",
    "WidgetRuntimeStatus",
    "WidgetRuntimePoller",
    "project_overlay_widget_records",
    "start_runtime_widgets",
]
