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

"""Host policy for runtime V2."""

from __future__ import annotations

from runtimeV2.contracts import HostAppIdentity, HostShell
from runtimeV2.plugins.schemas.manifest import PluginManifest


HOST_PLUGIN_ID = "tinyui"


def build_host_shell(manifests: dict[str, PluginManifest]) -> HostShell:
    """Build the host shell read-model from plugin manifests."""

    host_manifest = manifests.get(HOST_PLUGIN_ID)
    if host_manifest is None:
        raise RuntimeError(f"Host plugin manifest not found: {HOST_PLUGIN_ID}")
    if host_manifest.plugin_type != "host":
        raise RuntimeError(f"Plugin '{HOST_PLUGIN_ID}' is not a host plugin")
    if host_manifest.ui is None or not host_manifest.ui.windows:
        raise RuntimeError(f"Host plugin '{HOST_PLUGIN_ID}' does not declare a window")

    main_window = host_manifest.ui.windows[0]
    identity = HostAppIdentity(
        app_id=host_manifest.plugin_id,
        app_version=host_manifest.version,
        app_title=main_window.title,
        app_icon=host_manifest.icon,
    )
    return HostShell(
        host_plugin_id=HOST_PLUGIN_ID,
        host_manifest=host_manifest,
        main_window=main_window,
        identity=identity,
    )
