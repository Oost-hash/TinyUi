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

"""Manifest schema registration for UI."""

from runtimeV2.manifest.schema_registry import ManifestSchemaRegistry
from runtimeV2.ui.schemas.manifest import AppManifest, ChromePolicy, MenuItem, MenuSeparator, StatusbarItemDecl, TabDecl, UiManifest


def register_ui_schemas(registry: ManifestSchemaRegistry) -> None:
    """Register UI-owned manifest schemas."""

    registry.register_schema("ui", owner_domain="ui", schema_type=UiManifest)
    registry.register_schema("ui.window", owner_domain="ui", schema_type=AppManifest)
    registry.register_schema("ui.chrome", owner_domain="ui", schema_type=ChromePolicy)
    registry.register_schema("ui.tab", owner_domain="ui", schema_type=TabDecl)
    registry.register_schema("ui.menu_item", owner_domain="ui", schema_type=MenuItem)
    registry.register_schema("ui.menu_separator", owner_domain="ui", schema_type=MenuSeparator)
    registry.register_schema("ui.statusbar_item", owner_domain="ui", schema_type=StatusbarItemDecl)
