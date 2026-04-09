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

"""Mount packaged plugin runtimes to a runtime-friendly layout."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
import shutil
import sys
import zipfile

from pkg_runtime_host.contracts import MountedPkgRuntime
from pkg_runtime_host.manifest_lock import load_manifest_lock


PACKAGE_FORMAT = "compiled-v2"
APP_ID = "tinyui"


def is_packaged_plugin_dir(plugin_dir: Path) -> bool:
    """Return whether one directory looks like a packaged plugin root."""

    return (
        (plugin_dir / "_internal" / "manifest.toml").exists()
        and (plugin_dir / "manifest.lock").exists()
    )


def mount_packaged_plugin(plugin_dir: Path) -> MountedPkgRuntime:
    """Mount one packaged plugin into a runtime-friendly extracted form."""

    package_root = plugin_dir.resolve()
    manifest_path = package_root / "_internal" / "manifest.toml"
    lock_path = package_root / "manifest.lock"
    if not manifest_path.exists():
        raise FileNotFoundError(f"Packaged manifest not found: {manifest_path}")
    if not lock_path.exists():
        raise FileNotFoundError(f"Packaged manifest lock not found: {lock_path}")

    manifest_lock = load_manifest_lock(lock_path)
    if manifest_lock.package_format != PACKAGE_FORMAT:
        raise ValueError(
            f"Unsupported packaged plugin format '{manifest_lock.package_format}' for {manifest_lock.plugin_id}"
        )

    runtime_artifact = (package_root / manifest_lock.runtime_artifact).resolve()
    if not runtime_artifact.exists():
        raise FileNotFoundError(f"Packaged runtime artifact not found: {runtime_artifact}")

    runtime_sha256 = _sha256(runtime_artifact)
    if runtime_sha256 != manifest_lock.runtime_sha256:
        raise ValueError(
            f"Packaged runtime hash mismatch for {manifest_lock.plugin_id}: "
            f"expected {manifest_lock.runtime_sha256}, got {runtime_sha256}"
        )

    mount_root = _mount_root(manifest_lock.plugin_id, runtime_sha256)
    plugin_root = mount_root / "plugins" / manifest_lock.plugin_id
    if not plugin_root.exists():
        if mount_root.exists():
            shutil.rmtree(mount_root)
        mount_root.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(runtime_artifact) as archive:
            archive.extractall(mount_root)

    if not plugin_root.exists():
        raise RuntimeError(f"Mounted packaged plugin root not found after extraction: {plugin_root}")

    return MountedPkgRuntime(
        plugin_id=manifest_lock.plugin_id,
        package_root=package_root,
        manifest_path=manifest_path,
        import_root=mount_root,
        plugin_root=plugin_root,
        runtime_artifact=runtime_artifact,
        runtime_sha256=runtime_sha256,
    )


def _mount_root(plugin_id: str, runtime_sha256: str) -> Path:
    cache_root = _cache_root()
    return cache_root / plugin_id / runtime_sha256


def _cache_root() -> Path:
    if sys.platform == "win32":
        base = Path(os.getenv("APPDATA", str(Path.home())))
        return base / APP_ID / "pkg_runtime_host"
    xdg_cache = os.getenv("XDG_CACHE_HOME")
    if xdg_cache:
        return Path(xdg_cache) / APP_ID / "pkg_runtime_host"
    return Path.home() / ".cache" / APP_ID / "pkg_runtime_host"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
