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

"""Runtime V2 manifest domain."""

from runtimeV2.manifest.capabilities.connector_read import ManifestConnectorRead
from runtimeV2.manifest.capabilities.load import ManifestLoad
from runtimeV2.manifest.capabilities.manifest_read import ManifestRead
from runtimeV2.manifest.capabilities.overlay_read import ManifestOverlayRead
from runtimeV2.manifest.capabilities.settings_read import ManifestSettingsRead
from runtimeV2.manifest.capabilities.ui_read import ManifestUiRead
from runtimeV2.manifest.registry import ManifestRecord, ManifestRegistry
from runtimeV2.manifest.schema_registry import ManifestSchemaRecord, ManifestSchemaRegistry
from runtimeV2.manifest.startup import ManifestStartupResult

__all__ = [
    "ManifestConnectorRead",
    "ManifestLoad",
    "ManifestOverlayRead",
    "ManifestRead",
    "ManifestRecord",
    "ManifestRegistry",
    "ManifestSchemaRecord",
    "ManifestSchemaRegistry",
    "ManifestSettingsRead",
    "ManifestStartupResult",
    "ManifestUiRead",
]
