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

"""Capability registration for runtime V2 plugins."""

from __future__ import annotations

from dataclasses import dataclass

from runtimeV2.plugins.capabilities.connector_decl_read import PluginConnectorDeclRead
from runtimeV2.plugins.capabilities.discovery import PluginDiscoveryCapability
from runtimeV2.plugins.capabilities.icon import PluginIconCapability
from runtimeV2.plugins.capabilities.manifest_read import PluginManifestRead
from runtimeV2.plugins.capabilities.overlay_decl_read import PluginOverlayDeclRead
from runtimeV2.plugins.capabilities.settings_spec_read import PluginSettingsSpecRead
from runtimeV2.plugins.capabilities.ui_manifest_read import PluginUiManifestRead
from runtimeV2.plugins.registry import PluginRegistry


@dataclass(frozen=True)
class PluginCapabilities:
    """Capabilities exposed by the plugins discovery slice."""

    discovery: PluginDiscoveryCapability
    manifest_read: PluginManifestRead
    settings_spec_read: PluginSettingsSpecRead
    ui_manifest_read: PluginUiManifestRead
    connector_decl_read: PluginConnectorDeclRead
    overlay_decl_read: PluginOverlayDeclRead
    icon: PluginIconCapability


def register_plugin_capabilities(registry: PluginRegistry) -> PluginCapabilities:
    """Create plugin discovery/read capabilities."""

    return PluginCapabilities(
        discovery=PluginDiscoveryCapability(registry),
        manifest_read=PluginManifestRead(registry),
        settings_spec_read=PluginSettingsSpecRead(registry),
        ui_manifest_read=PluginUiManifestRead(registry),
        connector_decl_read=PluginConnectorDeclRead(registry),
        overlay_decl_read=PluginOverlayDeclRead(registry),
        icon=PluginIconCapability(registry),
    )
