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
"""Session runtime for active providers and consumer bindings."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from tinycore.capabilities.registry import (
    CapabilityBinding,
    CapabilityProvider,
    CapabilityRegistry,
)
from tinycore.plugin.manifest import ProviderRequest
from .control import ProviderControlService


@dataclass(frozen=True)
class ProviderHandle:
    """Active provider instance registered in the session."""

    name: str
    exports: tuple[str, ...]
    provider: Any


@dataclass(frozen=True)
class ConsumerBindingSet:
    """Resolved capability bindings for one consumer plugin."""

    consumer_name: str
    requires: tuple[str, ...]
    resolved: dict[str, CapabilityBinding] = field(default_factory=dict)
    missing: tuple[str, ...] = ()

    def get(self, capability: str) -> CapabilityBinding | None:
        """Return the binding for a required capability, if resolved."""
        if capability not in self.requires:
            raise KeyError(f"Capability '{capability}' was not declared in requires")
        return self.resolved.get(capability)

    def require(self, capability: str) -> CapabilityBinding:
        """Return the binding for a required capability or raise KeyError."""
        binding = self.get(capability)
        if binding is None:
            raise KeyError(f"No provider bound for capability '{capability}'")
        return binding

    def is_satisfied(self) -> bool:
        """Return True when all required capabilities resolved."""
        return not self.missing


class SessionRuntime:
    """Owns active providers and resolved consumer bindings."""

    def __init__(self, capabilities: CapabilityRegistry) -> None:
        self._capabilities = capabilities
        self._providers: dict[str, ProviderHandle] = {}
        self._bindings_by_consumer: dict[str, ConsumerBindingSet] = {}
        self.controls = ProviderControlService(self)

    def register_provider(
        self,
        provider_name: str,
        provider: Any,
        exports: tuple[str, ...],
    ) -> ProviderHandle:
        """Register an active provider and its exported capabilities."""
        handle = ProviderHandle(
            name=provider_name,
            exports=exports,
            provider=provider,
        )
        self._providers[provider_name] = handle
        self._capabilities.register_many(provider_name, exports, provider)
        return handle

    def bind_consumer(
        self,
        consumer_name: str,
        requires: tuple[str, ...],
        provider_requests: tuple[ProviderRequest, ...] = (),
    ) -> ConsumerBindingSet:
        """Resolve and store bindings for one consumer plugin."""
        resolved: dict[str, CapabilityBinding] = {}
        missing: list[str] = []
        request_map = {request.capability: request for request in provider_requests}
        for capability in requires:
            candidate = self._select_provider(capability, request_map.get(capability))
            if candidate is None:
                missing.append(capability)
                continue
            resolved[capability] = CapabilityBinding(
                capability=capability,
                provider_name=candidate.provider_name,
                provider=candidate.provider,
            )

        binding_set = ConsumerBindingSet(
            consumer_name=consumer_name,
            requires=requires,
            resolved=resolved,
            missing=tuple(missing),
        )
        self._bindings_by_consumer[consumer_name] = binding_set
        return binding_set

    def provider(self, provider_name: str) -> ProviderHandle | None:
        """Return an active provider by name."""
        return self._providers.get(provider_name)

    def providers(self) -> list[ProviderHandle]:
        """Return all active providers."""
        return list(self._providers.values())

    def provider_items(self) -> list[tuple[str, ProviderHandle]]:
        """Return all active providers keyed by provider name."""
        return list(self._providers.items())

    def bindings_for(self, consumer_name: str) -> ConsumerBindingSet:
        """Return the binding set for a consumer plugin."""
        return self._bindings_by_consumer.get(
            consumer_name,
            ConsumerBindingSet(consumer_name=consumer_name, requires=()),
        )

    def update_providers(self) -> list[tuple[str, str]]:
        """Tick all provider runtimes that expose ``update()``.

        Returns:
            A list of ``(provider_name, error)`` pairs for providers that failed.
        """
        errors: list[tuple[str, str]] = []
        for provider_name, handle in self._providers.items():
            update = getattr(handle.provider, "update", None)
            if not callable(update):
                continue
            try:
                update()
            except Exception as exc:
                errors.append((provider_name, str(exc)))
        return errors

    def _select_provider(
        self,
        capability: str,
        request: ProviderRequest | None,
    ) -> CapabilityProvider | None:
        """Return the registered provider for one capability plus optional selector."""
        provider = self._capabilities.provider_for(capability)
        if provider is None:
            return None
        if request is not None and request.provider and provider.provider_name != request.provider:
            return None
        if request is not None and request.source:
            select_source = getattr(provider.provider, "request_source", None)
            if callable(select_source):
                owner = f"manifest:{provider.provider_name}:{capability}"
                selected = bool(select_source(owner, request.source))
                if not selected:
                    return None
        return provider
