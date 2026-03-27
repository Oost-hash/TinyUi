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
from typing import TYPE_CHECKING, Any

from tinycore.capabilities.registry import (
    CapabilityBinding,
    CapabilityProvider,
    CapabilityRegistry,
)
from tinycore.plugin.manifest import ProviderRequest
from tinycore.runtime.models import RuntimeState
from tinycore.runtime.unit_ids import provider_capability_unit_id, provider_runtime_unit_id
from .control import ProviderControlService

if TYPE_CHECKING:
    from tinycore.runtime.registry import RuntimeRegistry


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
        self._active_consumers: set[str] = set()
        self._active_provider_names: set[str] = set()
        self._runtime_registry: RuntimeRegistry | None = None
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
        self._refresh_active_providers()
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
        if consumer_name in self._active_consumers:
            self._refresh_active_providers()
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

    def active_provider_items(self) -> list[tuple[str, ProviderHandle]]:
        """Return providers that are currently activated by active consumers."""
        return [
            (provider_name, handle)
            for provider_name, handle in self._providers.items()
            if provider_name in self._active_provider_names
        ]

    def bindings_for(self, consumer_name: str) -> ConsumerBindingSet:
        """Return the binding set for a consumer plugin."""
        return self._bindings_by_consumer.get(
            consumer_name,
            ConsumerBindingSet(consumer_name=consumer_name, requires=()),
        )

    def activate_consumer(self, consumer_name: str) -> None:
        """Mark one consumer runtime as active for provider update purposes."""
        self._active_consumers.add(consumer_name)
        self._refresh_active_providers()

    def deactivate_consumer(self, consumer_name: str) -> None:
        """Mark one consumer runtime as inactive for provider update purposes."""
        self._active_consumers.discard(consumer_name)
        self._refresh_active_providers()

    def active_provider_names(self) -> tuple[str, ...]:
        """Return provider names currently active through consumer bindings."""
        return tuple(sorted(self._active_provider_names))

    def attach_runtime_registry(self, registry: RuntimeRegistry) -> None:
        """Attach runtime graph tracking for provider runtime and capability units."""
        self._runtime_registry = registry
        self._sync_provider_runtime_states(set(), self._active_provider_names)

    def update_providers(self) -> list[tuple[str, str]]:
        """Tick all provider runtimes that expose ``update()``.

        Returns:
            A list of ``(provider_name, error)`` pairs for providers that failed.
        """
        errors: list[tuple[str, str]] = []
        for provider_name, handle in self.active_provider_items():
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

    def _refresh_active_providers(self) -> None:
        previous = set(self._active_provider_names)
        active: set[str] = set()
        for consumer_name in self._active_consumers:
            bindings = self._bindings_by_consumer.get(consumer_name)
            if bindings is None:
                continue
            active.update(binding.provider_name for binding in bindings.resolved.values())
        self._active_provider_names = active
        self._sync_provider_runtime_states(previous, active)

    def _sync_provider_runtime_states(self, previous: set[str], current: set[str]) -> None:
        if self._runtime_registry is None:
            return

        for provider_name in previous - current:
            self._set_provider_runtime_state(provider_name, "idle")
        for provider_name in current - previous:
            self._set_provider_runtime_state(provider_name, "running")
        for provider_name in current & previous:
            self._set_provider_runtime_state(provider_name, "running")

    def _set_provider_runtime_state(self, provider_name: str, state: RuntimeState) -> None:
        if self._runtime_registry is None:
            return
        handle = self._providers.get(provider_name)
        runtime_unit_id = provider_runtime_unit_id(provider_name)
        if self._runtime_registry.get(runtime_unit_id) is not None:
            self._runtime_registry.set_state(runtime_unit_id, state)
        if handle is None:
            return
        for capability in handle.exports:
            capability_unit_id = provider_capability_unit_id(provider_name, capability)
            if self._runtime_registry.get(capability_unit_id) is not None:
                self._runtime_registry.set_state(capability_unit_id, state)
