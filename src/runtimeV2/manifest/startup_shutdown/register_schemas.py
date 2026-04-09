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

"""Manifest schema registration orchestration."""

from runtimeV2.connectors.startup_shutdown.register_schemas import register_connector_schemas
from runtimeV2.manifest.schema_registry import ManifestSchemaRegistry
from runtimeV2.persistence.startup_shutdown.register_schemas import register_persistence_schemas
from runtimeV2.plugins.startup_shutdown.register_schemas import register_plugin_schemas
from runtimeV2.ui.startup_shutdown.register_schemas import register_ui_schemas
from runtimeV2.widgets.startup_shutdown.register_schemas import register_widget_schemas


def register_manifest_schemas(registry: ManifestSchemaRegistry) -> None:
    """Register manifest schemas owned by runtime V2 domains."""

    register_plugin_schemas(registry)
    register_ui_schemas(registry)
    register_connector_schemas(registry)
    register_widget_schemas(registry)
    register_persistence_schemas(registry)

