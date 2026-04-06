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

"""Plugin root manifest dataclasses."""

from __future__ import annotations

from dataclasses import dataclass, field

from app_schema.connector import ConnectorManifest
from app_schema.overlay import OverlayManifest
from app_schema.ui import SettingDecl, UiManifest


@dataclass(frozen=True)
class PluginManifest:
    plugin_id: str
    plugin_type: str
    version: str
    author: str
    description: str
    icon: str
    requires: list[str]
    settings: list[SettingDecl] = field(default_factory=list)
    ui: UiManifest | None = None
    connector: ConnectorManifest | None = None
    overlay: OverlayManifest | None = None
