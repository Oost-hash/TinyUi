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

"""Mutable image source registry for the paths domain."""

from __future__ import annotations

from runtimeV2.paths.image_source import ImageSource


class ImageSourceRegistry:
    """Registry for image sources that supports both dev and QRC modes.

    Populated after plugin discovery so plugins can declare images in their
    manifest rather than hardcoding paths in the paths domain.
    """

    def __init__(self) -> None:
        self._sources: dict[str, ImageSource] = {}

    def register(self, name: str, source: ImageSource) -> None:
        """Register an image source under a logical name."""
        self._sources[name] = source

    def get(self, name: str) -> ImageSource:
        """Return a registered image source by name."""
        try:
            return self._sources[name]
        except KeyError as exc:
            raise KeyError(f"Image source '{name}' is not registered") from exc

    def names(self) -> list[str]:
        """Return all registered image source names."""
        return list(self._sources.keys())

    def has(self, name: str) -> bool:
        """Return whether an image source is registered."""
        return name in self._sources
