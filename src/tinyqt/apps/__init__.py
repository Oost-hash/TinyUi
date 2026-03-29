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
"""Application-specific compositions and manifests hosted by tinyqt."""

from tinycore.paths import AppPaths

from tinyqt.manifests import TinyQtAppManifest

from .devtools import build_tinyqt_devtools_manifest
from .settings import build_tinyqt_settings_manifest
from .tinyui import (
    TINYUI_HOST_ASSEMBLY,
    build_tinyui_launch_spec,
    build_tinyui_manifest,
)


def build_first_party_manifests(paths: AppPaths) -> dict[str, TinyQtAppManifest]:
    """Return the static manifest map for first-party hosted surfaces."""
    tinyui_manifest = build_tinyui_manifest(paths)
    tinyqt_settings_manifest = build_tinyqt_settings_manifest(paths)
    tinyqt_devtools_manifest = build_tinyqt_devtools_manifest(paths)
    return {
        tinyui_manifest.app_id: tinyui_manifest,
        tinyqt_settings_manifest.app_id: tinyqt_settings_manifest,
        tinyqt_devtools_manifest.app_id: tinyqt_devtools_manifest,
    }


def get_first_party_manifest(paths: AppPaths, app_id: str) -> TinyQtAppManifest:
    """Resolve a first-party hosted surface manifest by id."""
    manifests = build_first_party_manifests(paths)
    try:
        return manifests[app_id]
    except KeyError as exc:
        raise KeyError(f"Unknown TinyQt first-party manifest '{app_id}'") from exc

__all__ = [
    "TINYUI_HOST_ASSEMBLY",
    "build_tinyui_launch_spec",
    "build_first_party_manifests",
    "get_first_party_manifest",
    "build_tinyui_manifest",
    "build_tinyqt_settings_manifest",
    "build_tinyqt_devtools_manifest",
]
