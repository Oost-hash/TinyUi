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

"""Registry for shared runtime host projections."""

from __future__ import annotations

from typing import TypeVar

from runtimeV2.runtime import RuntimeV2

T = TypeVar("T")


class SharedRuntimeHostRegistry:
    """Store shared and host-specific runtime host projections."""

    def __init__(self, runtime: RuntimeV2) -> None:
        self._runtime = runtime
        self._capabilities: dict[str, object] = {}

    @property
    def runtime(self) -> RuntimeV2:
        """Return the runtime that backs this host registry."""

        return self._runtime

    def register_capability(self, name: str, capability: object) -> None:
        """Register one shared or host-specific projection capability."""

        if name in self._capabilities:
            raise ValueError(f"Shared runtime host capability '{name}' is already registered")
        self._capabilities[name] = capability

    def capability(self, name: str, capability_type: type[T]) -> T:
        """Return one registered host projection capability."""

        capability = self._capabilities[name]
        if not isinstance(capability, capability_type):
            raise TypeError(
                f"Shared runtime host capability '{name}' is not of type {capability_type.__name__}"
            )
        return capability

    def has_capability(self, name: str) -> bool:
        """Return whether one projection capability is registered."""

        return name in self._capabilities


def create_shared_runtime_host_registry(runtime: RuntimeV2) -> SharedRuntimeHostRegistry:
    """Create an empty shared runtime host registry for one host."""

    return SharedRuntimeHostRegistry(runtime)
