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
"""ProviderRegistry — type-keyed provider lookup."""

from __future__ import annotations

from typing import TypeVar

from .protocol import Provider

T = TypeVar("T")


class ProviderRegistry:
    """Type-keyed registry for pull-based providers."""

    def __init__(self):
        self._providers: dict[type, Provider] = {}

    def register(self, data_type: type[T], provider: Provider[T]) -> None:
        """Register a provider for a data type."""
        self._providers[data_type] = provider

    def get(self, data_type: type[T]) -> T:
        """Pull current value from the provider. Raises KeyError if not registered."""
        if data_type not in self._providers:
            raise KeyError(f"No provider registered for {data_type}")
        return self._providers[data_type].get()

    def has(self, data_type: type) -> bool:
        """Check if a provider is registered for this type."""
        return data_type in self._providers
