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

"""Helpers for loading packaged plugin distributions."""

from __future__ import annotations

import shutil
import tomllib
import zipfile
from dataclasses import dataclass
from pathlib import Path

from runtime.app.paths import AppPaths


@dataclass(frozen=True)
class PackagedPluginPaths:
    """Resolved filesystem paths for a packaged plugin."""

    manifest_path: Path
    plugin_root: Path
    import_root: Path | None


def resolve_packaged_plugin(plugin_dir: Path, paths: AppPaths) -> PackagedPluginPaths | None:
    """Resolve a packaged plugin directory into an extracted runtime layout."""
    manifest_path = plugin_dir / "_internal" / "manifest.toml"
    manifest_lock = plugin_dir / "manifest.lock"
    if not manifest_path.exists() or not manifest_lock.exists():
        return None

    lock_data = tomllib.loads(manifest_lock.read_text(encoding="utf-8"))
    runtime_artifact = lock_data.get("runtime_artifact")
    plugin_name = plugin_dir.name
    if not isinstance(runtime_artifact, str) or not runtime_artifact.strip():
        runtime_artifact = f"runtime/{plugin_name}.pkg"

    artifact_path = plugin_dir / runtime_artifact
    if not artifact_path.exists():
        raise FileNotFoundError(f"Packaged plugin runtime artifact not found: {artifact_path}")

    extraction_root = paths.data_dir / "_compiled_plugins" / plugin_name
    if extraction_root.exists():
        shutil.rmtree(extraction_root)
    extraction_root.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(artifact_path) as archive:
        archive.extractall(extraction_root)

    plugin_root = extraction_root / "plugins" / plugin_name
    if not plugin_root.exists():
        return PackagedPluginPaths(
            manifest_path=manifest_path,
            plugin_root=manifest_path.parent,
            import_root=None,
        )

    return PackagedPluginPaths(
        manifest_path=manifest_path,
        plugin_root=plugin_root,
        import_root=extraction_root,
    )
