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

"""Plugin manifest parser entry for runtime V2."""

from __future__ import annotations

from pathlib import Path

from runtime.manifest import load_plugin_manifest as _load_plugin_manifest
from runtimeV2.plugins.schemas import PluginManifest


def load_plugin_manifest(path: Path, *, resource_root: Path | None = None) -> PluginManifest:
    """Load a plugin manifest through the runtime V2 plugins domain."""

    return _load_plugin_manifest(path, resource_root=resource_root)
