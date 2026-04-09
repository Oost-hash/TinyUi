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

"""Plugin root manifest schema."""

from __future__ import annotations

from dataclasses import dataclass, field

from runtimeV2.connectors.schemas.manifest import ConnectorManifest
from runtimeV2.persistence.schemas.settings import SettingDecl
from runtimeV2.ui.schemas.manifest import UiManifest
from runtimeV2.widgets.schemas.manifest import OverlayManifest


@dataclass(frozen=True)
class PluginManifest:
    """Root plugin manifest container."""

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
