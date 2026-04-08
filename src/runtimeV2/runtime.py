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

"""Runtime V2 prototype orchestrator."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TypeVar


T = TypeVar("T")


@dataclass(frozen=True)
class DomainRegistration:
    """A registered runtime V2 domain."""

    name: str
    description: str = ""


class RuntimeV2:
    """Small runtime V2 orchestrator prototype.

    This class intentionally does not replace the active Runtime yet. It is a
    visible sketch of the v0.5.5 direction: runtime owns orchestration and
    registries, while domains own their own startup and capabilities.
    """

    def __init__(self) -> None:
        self._domains: dict[str, DomainRegistration] = {}
        self._domain_results: dict[str, object] = {}
        self._capabilities: dict[str, object] = {}

    def register_domain(self, name: str, *, description: str = "") -> None:
        """Register a domain with the runtime orchestrator."""

        self._domains[name] = DomainRegistration(name=name, description=description)

    def domain_names(self) -> list[str]:
        """Return registered domain names in registration order."""

        return list(self._domains)

    def register_domain_result(self, name: str, result: object) -> None:
        """Store the startup result owned by a domain."""

        if name not in self._domains:
            self.register_domain(name)
        self._domain_results[name] = result

    def domain_result(self, name: str, result_type: type[T]) -> T:
        """Return a typed domain result."""

        result = self._domain_results.get(name)
        if not isinstance(result, result_type):
            raise KeyError(f"Domain result '{name}' is not available as {result_type.__name__}")
        return result

    def register_capability(self, name: str, capability: object) -> None:
        """Register a capability exposed by runtime or one of its domains."""

        self._capabilities[name] = capability

    def capability(self, name: str, capability_type: type[T]) -> T:
        """Return a typed capability."""

        capability = self._capabilities.get(name)
        if not isinstance(capability, capability_type):
            raise KeyError(f"Capability '{name}' is not available as {capability_type.__name__}")
        return capability
