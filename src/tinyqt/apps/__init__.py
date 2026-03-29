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

from .devtools import build_tinyqt_devtools_manifest
from .registry import (
    FIRST_PARTY_FEATURES,
    FirstPartyFeatureSpec,
    build_first_party_manifests,
    get_first_party_manifest,
)
from .settings import build_tinyqt_settings_manifest
from .tinyui import (
    TINYUI_HOST_ASSEMBLY,
    build_tinyui_launch_spec,
    build_tinyui_manifest,
)

__all__ = [
    "FIRST_PARTY_FEATURES",
    "FirstPartyFeatureSpec",
    "TINYUI_HOST_ASSEMBLY",
    "build_tinyui_launch_spec",
    "build_first_party_manifests",
    "get_first_party_manifest",
    "build_tinyui_manifest",
    "build_tinyqt_settings_manifest",
    "build_tinyqt_devtools_manifest",
]
