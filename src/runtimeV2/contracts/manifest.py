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

"""Public manifest contracts used outside the manifest domain."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol, runtime_checkable

from runtimeV2.connectors.schemas.manifest import ConnectorManifest
from runtimeV2.persistence.schemas.settings import SettingDecl
from runtimeV2.plugins.schemas.manifest import PluginManifest
from runtimeV2.ui.schemas.manifest import AppManifest, MenuItem, MenuSeparator, StatusbarItemDecl, TabDecl
from runtimeV2.widgets.schemas.manifest import OverlayManifest


@runtime_checkable
class ManifestReader(Protocol):
    """Public contract for reading loaded plugin manifests."""

    def plugin_manifest(self, plugin_id: str) -> PluginManifest | None:
        """Return one loaded manifest."""
        ...

    def all_manifests(self) -> dict[str, PluginManifest]:
        """Return all loaded manifests."""
        ...

    def plugin_roles(self) -> dict[str, str]:
        """Return plugin roles by plugin id."""
        ...

    def resource_root(self, plugin_id: str) -> Path | None:
        """Return one manifest resource root."""
        ...


@runtime_checkable
class ManifestLoader(Protocol):
    """Public contract for loading and registering plugin manifests."""

    def load_manifest(self, path: Path, *, resource_root: Path, source: str) -> PluginManifest:
        """Load and register one plugin manifest."""
        ...


@runtime_checkable
class ManifestConnectorReader(Protocol):
    """Public contract for reading connector declarations from plugin manifests."""

    def connector_declarations(self) -> dict[str, ConnectorManifest]:
        """Return connector declarations by plugin id."""
        ...


@runtime_checkable
class ManifestOverlayReader(Protocol):
    """Public contract for reading overlay declarations from plugin manifests."""

    def overlay_declarations(self) -> dict[str, OverlayManifest]:
        """Return overlay declarations by plugin id."""
        ...


@runtime_checkable
class ManifestSettingsReader(Protocol):
    """Public contract for reading settings specs declared by plugin manifests."""

    def settings_specs(self) -> dict[str, list[SettingDecl]]:
        """Return settings specs by plugin id."""
        ...


@runtime_checkable
class ManifestUiReader(Protocol):
    """Public contract for reading UI declarations from plugin manifests."""

    def windows(self) -> dict[str, list[AppManifest]]:
        """Return manifest windows by plugin id."""
        ...

    def tabs(self) -> dict[str, list[TabDecl]]:
        """Return manifest tabs by plugin id."""
        ...

    def menus(self) -> dict[str, list[MenuItem | MenuSeparator]]:
        """Return plugin menu declarations by plugin id."""
        ...

    def statusbar_items(self) -> dict[str, list[StatusbarItemDecl]]:
        """Return statusbar item declarations by window id."""
        ...
