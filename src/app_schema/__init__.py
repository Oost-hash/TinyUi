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

"""Public app schema exports."""

from app_schema.connector import ConnectorGameDecl, ConnectorManifest, ConnectorServiceDecl
from app_schema.overlay import OverlayManifest, OverlayWidgetDecl
from app_schema.plugin import PluginManifest
from app_schema.ui import (
    AppManifest,
    ChromePolicy,
    MenuItem,
    MenuSeparator,
    SettingDecl,
    StatusbarItemDecl,
    TabDecl,
    UiManifest,
)

__all__ = [
    "AppManifest",
    "ChromePolicy",
    "ConnectorGameDecl",
    "ConnectorManifest",
    "ConnectorServiceDecl",
    "MenuItem",
    "MenuSeparator",
    "OverlayManifest",
    "OverlayWidgetDecl",
    "PluginManifest",
    "SettingDecl",
    "StatusbarItemDecl",
    "TabDecl",
    "UiManifest",
]
