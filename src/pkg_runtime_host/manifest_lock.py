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

"""Read manifest.lock metadata for packaged plugins."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import tomllib


@dataclass(frozen=True)
class ManifestLock:
    """Normalized packaged runtime lock metadata."""

    plugin_id: str
    version: str
    package_format: str
    runtime_artifact: str
    runtime_sha256: str


def load_manifest_lock(path: Path) -> ManifestLock:
    """Load one packaged plugin manifest lock."""

    with path.open("rb") as file:
        data = tomllib.load(file)

    return ManifestLock(
        plugin_id=_require_string(data, "plugin", path),
        version=_require_string(data, "version", path),
        package_format=_require_string(data, "package_format", path),
        runtime_artifact=_require_string(data, "runtime_artifact", path),
        runtime_sha256=_require_string(data, "runtime_sha256", path),
    )


def _require_string(data: dict[str, object], key: str, path: Path) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Manifest lock '{path}' must define '{key}' as a non-empty string")
    return value
