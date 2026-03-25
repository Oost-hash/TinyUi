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
"""Capability registry for provider exports and consumer bindings."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class CapabilityBinding:
    """Resolved provider for a capability."""

    capability: str
    provider_name: str
    provider: Any


class CapabilityRegistry:
    """Registers exported capabilities and resolves consumer requirements."""

    def __init__(self) -> None:
        self._capabilities: dict[str, CapabilityBinding] = {}

    def register(self, capability: str, provider_name: str, provider: Any) -> None:
        """Register one exported capability for a provider."""
        existing = self._capabilities.get(capability)
        if existing is not None and existing.provider_name != provider_name:
            raise ValueError(
                f"Capability '{capability}' is already provided by '{existing.provider_name}'"
            )
        self._capabilities[capability] = CapabilityBinding(
            capability=capability,
            provider_name=provider_name,
            provider=provider,
        )

    def register_many(self, provider_name: str, capabilities: tuple[str, ...], provider: Any) -> None:
        """Register all exported capabilities for one provider."""
        for capability in capabilities:
            self.register(capability, provider_name, provider)

    def get(self, capability: str) -> CapabilityBinding | None:
        """Return the registered provider binding for a capability, if any."""
        return self._capabilities.get(capability)

    def require(self, capability: str) -> CapabilityBinding:
        """Return a registered capability binding or raise KeyError."""
        binding = self.get(capability)
        if binding is None:
            raise KeyError(f"No provider registered for capability '{capability}'")
        return binding

    def all(self) -> list[CapabilityBinding]:
        """Return all registered capability bindings."""
        return list(self._capabilities.values())
