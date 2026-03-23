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
"""Plugin manifest — declarative description of a plugin.

Each plugin directory contains a plugin.toml that declares its name,
Python module/class, optional connector, and optional widget definitions.
The composition root reads manifests to wire everything up without
importing any plugin-specific code itself.

Example plugin.toml:

    name   = "demo"
    module = "plugins.demo"
    class  = "DemoPlugin"

    [connector]
    module = "plugins.demo.connector.lmu"
    class  = "LMUConnector"

    [widgets]
    file = "widgets.toml"
"""

from __future__ import annotations

import importlib
import tomllib
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ConnectorDecl:
    """Declares which connector class to instantiate in the host process."""
    module:     str
    class_name: str

    def create(self):
        """Import and instantiate the connector."""
        mod = importlib.import_module(self.module)
        cls = getattr(mod, self.class_name)
        return cls()


@dataclass
class PluginManifest:
    """Parsed contents of a plugin.toml."""
    name:       str
    module:     str
    class_name: str
    plugin_dir: Path
    connector:  ConnectorDecl | None = field(default=None)
    widgets_file: str | None         = field(default=None)

    def widgets_path(self) -> Path | None:
        """Absolute path to the widgets TOML file, or None if not declared."""
        if not self.widgets_file:
            return None
        return self.plugin_dir / self.widgets_file


def load_manifest(path: Path) -> PluginManifest:
    """Parse a plugin.toml file and return a PluginManifest."""
    with path.open("rb") as f:
        data = tomllib.load(f)

    connector = None
    if "connector" in data:
        c = data["connector"]
        connector = ConnectorDecl(
            module=c["module"],
            class_name=c["class"],
        )

    return PluginManifest(
        name=data["name"],
        module=data["module"],
        class_name=data["class"],
        plugin_dir=path.parent,
        connector=connector,
        widgets_file=data.get("widgets", {}).get("file"),
    )


def scan_plugins(plugins_dir: Path) -> list[PluginManifest]:
    """Return manifests for all plugins found in plugins_dir.

    Scans for plugin.toml in immediate subdirectories, sorted by name.
    """
    manifests = []
    for manifest_path in sorted(plugins_dir.glob("*/plugin.toml")):
        manifests.append(load_manifest(manifest_path))
    return manifests
