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

"""QML property schema for runtime V2 UI."""

from __future__ import annotations

from runtimeV2.contracts import QmlPropertyPlan


def register_qml_property_plan() -> list[QmlPropertyPlan]:
    """Return the runtime capability to QML property mapping."""

    return [
        QmlPropertyPlan("manifest_read", "manifestRead"),
        QmlPropertyPlan("settings_read", "settingsRead"),
        QmlPropertyPlan("settings_write", "settingsWrite"),
        QmlPropertyPlan("connector_read", "connectorRead"),
        QmlPropertyPlan("connector_write", "connectorActions"),
        QmlPropertyPlan("plugin_active_read", "pluginActive"),
        QmlPropertyPlan("plugin_state_read", "pluginState"),
        QmlPropertyPlan("widget_records_read", "widgetRecords"),
        QmlPropertyPlan("widget_visibility_read", "widgetVisibility"),
        QmlPropertyPlan("widget_config_read", "widgetConfigRead"),
        QmlPropertyPlan("widget_config_write", "widgetConfigWrite"),
        QmlPropertyPlan("window_records_read", "windowRecords"),
        QmlPropertyPlan("panel_state_read", "panelState"),
        QmlPropertyPlan("render_status_read", "renderStatus"),
        QmlPropertyPlan("ui_chrome_model_read", "uiChrome"),
    ]
