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

"""Runtime-owned facts and bound provider access for plugin participation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from tinyplugins.manifest import ProviderRequest

from .exports import ExportBinding, ParticipantExports


def _float_or_zero(value: object) -> float:
    return float(value) if isinstance(value, int | float) else 0.0


@dataclass(frozen=True)
class ProviderRuntimeHandle:
    """Active provider instance registered in runtime participation."""

    name: str
    exports: tuple[str, ...]
    provider: Any


@dataclass(frozen=True)
class ParticipantBindingSet:
    """Resolved export bindings for one plugin participant."""

    participant_name: str
    requires: tuple[str, ...]
    resolved: dict[str, ExportBinding] = field(default_factory=dict)
    missing: tuple[str, ...] = ()

    def get(self, export_name: str) -> ExportBinding | None:
        """Return the binding for one declared export requirement, if resolved."""
        if export_name not in self.requires:
            raise KeyError(f"Export '{export_name}' was not declared in requires")
        return self.resolved.get(export_name)

    def require(self, export_name: str) -> ExportBinding:
        """Return the binding for one declared export requirement or raise KeyError."""
        binding = self.get(export_name)
        if binding is None:
            raise KeyError(f"No provider bound for export '{export_name}'")
        return binding

    def is_satisfied(self) -> bool:
        """Return True when all required exports resolved."""
        return not self.missing


@dataclass(frozen=True)
class ProviderDemoConfig:
    """Provider demo-mode tuning values exposed to UI adapters."""

    minimum: float = 0.0
    maximum: float = 0.0
    speed: float = 0.0


@dataclass(frozen=True)
class _ExportProvider:
    """Registered provider for one exported runtime surface."""

    export_name: str
    provider_name: str
    provider: object


class _ExportRegistry:
    """Register exported surfaces and resolve providers by export name."""

    def __init__(self) -> None:
        self._exports: dict[str, _ExportProvider] = {}

    def register(
        self,
        export_name: str,
        provider_name: str,
        provider: object,
    ) -> None:
        existing = self._exports.get(export_name)
        if existing is not None and existing.provider_name != provider_name:
            raise ValueError(
                f"Export '{export_name}' is already owned by provider "
                f"'{existing.provider_name}', cannot also register '{provider_name}'"
            )
        self._exports[export_name] = _ExportProvider(
            export_name=export_name,
            provider_name=provider_name,
            provider=provider,
        )

    def register_many(
        self,
        provider_name: str,
        export_names: tuple[str, ...],
        provider: object,
    ) -> None:
        for export_name in export_names:
            self.register(export_name, provider_name, provider)

    def provider_for(self, export_name: str) -> _ExportProvider | None:
        return self._exports.get(export_name)


class _BoundProviderControls:
    """Provider-bound access surface backed by participation facts."""

    def __init__(self, facts: PluginParticipationFacts) -> None:
        self._facts = facts

    def provider_name_for(self, participant_name: str, export_name: str) -> str:
        binding = self._binding(participant_name, export_name)
        return binding.provider_name if binding is not None else ""

    def supports_demo_mode(self, participant_name: str, export_name: str) -> bool:
        provider = self._provider(participant_name, export_name)
        if provider is None:
            return False
        supports_demo = getattr(provider, "supports_demo_mode", None)
        return bool(supports_demo()) if callable(supports_demo) else False

    def request_demo_mode(self, participant_name: str, export_name: str, owner: str) -> bool:
        provider = self._provider(participant_name, export_name)
        request_demo_mode = getattr(provider, "request_demo_mode", None) if provider is not None else None
        if not callable(request_demo_mode):
            return False
        request_demo_mode(owner)
        return True

    def release_demo_mode(self, participant_name: str, export_name: str, owner: str) -> bool:
        provider = self._provider(participant_name, export_name)
        release_demo_mode = getattr(provider, "release_demo_mode", None) if provider is not None else None
        if not callable(release_demo_mode):
            return False
        release_demo_mode(owner)
        return True

    def provider_mode(self, participant_name: str, export_name: str) -> str:
        provider = self._provider(participant_name, export_name)
        if provider is None:
            return "missing"
        mode = getattr(provider, "mode", None)
        return str(mode()) if callable(mode) else "real"

    def active_game(self, participant_name: str, export_name: str) -> str:
        provider = self._provider(participant_name, export_name)
        if provider is None:
            return "none"
        active_game = getattr(provider, "active_game", None)
        return str(active_game()) if callable(active_game) else "unknown"

    def demo_config(self, participant_name: str, export_name: str) -> ProviderDemoConfig:
        provider = self._provider(participant_name, export_name)
        if provider is None:
            return ProviderDemoConfig()
        return ProviderDemoConfig(
            minimum=self._call_float(provider, "demo_min"),
            maximum=self._call_float(provider, "demo_max"),
            speed=self._call_float(provider, "demo_speed"),
        )

    def set_demo_min(self, participant_name: str, export_name: str, value: float) -> bool:
        return self._set_demo_value(participant_name, export_name, "set_demo_min", value)

    def set_demo_max(self, participant_name: str, export_name: str, value: float) -> bool:
        return self._set_demo_value(participant_name, export_name, "set_demo_max", value)

    def set_demo_speed(self, participant_name: str, export_name: str, value: float) -> bool:
        return self._set_demo_value(participant_name, export_name, "set_demo_speed", value)

    def _binding(self, participant_name: str, export_name: str):
        return self._facts.bindings_for(participant_name).get(export_name)

    def _provider(self, participant_name: str, export_name: str):
        binding = self._binding(participant_name, export_name)
        return binding.provider if binding is not None else None

    @staticmethod
    def _call_float(provider, name: str) -> float:
        getter = getattr(provider, name, None)
        return _float_or_zero(getter()) if callable(getter) else 0.0

    def _set_demo_value(self, participant_name: str, export_name: str, name: str, value: float) -> bool:
        provider = self._provider(participant_name, export_name)
        setter = getattr(provider, name, None) if provider is not None else None
        if not callable(setter):
            return False
        setter(value)
        return True


class _PluginBindingStore:
    """Internal backing store for runtime participation facts."""

    def __init__(self, exports: _ExportRegistry) -> None:
        self._exports = exports
        self._providers: dict[str, ProviderRuntimeHandle] = {}
        self._bindings_by_participant: dict[str, ParticipantBindingSet] = {}

    def register_provider(
        self,
        provider_name: str,
        provider: object,
        exports: tuple[str, ...],
    ) -> ProviderRuntimeHandle:
        handle = ProviderRuntimeHandle(
            name=provider_name,
            exports=exports,
            provider=provider,
        )
        self._providers[provider_name] = handle
        self._exports.register_many(provider_name, exports, provider)
        return handle

    def bind_participant(
        self,
        participant_name: str,
        requires: tuple[str, ...],
        provider_requests: tuple[ProviderRequest, ...] = (),
    ) -> ParticipantBindingSet:
        resolved: dict[str, ExportBinding] = {}
        missing: list[str] = []
        request_map = {request.capability: request for request in provider_requests}
        for export_name in requires:
            candidate = self._select_provider(export_name, request_map.get(export_name))
            if candidate is None:
                missing.append(export_name)
                continue
            resolved[export_name] = ExportBinding(
                export_name=export_name,
                provider_name=candidate.provider_name,
                provider=candidate.provider,
            )

        binding_set = ParticipantBindingSet(
            participant_name=participant_name,
            requires=requires,
            resolved=resolved,
            missing=tuple(missing),
        )
        self._bindings_by_participant[participant_name] = binding_set
        return binding_set

    def provider(self, provider_name: str) -> ProviderRuntimeHandle | None:
        return self._providers.get(provider_name)

    def providers(self) -> list[ProviderRuntimeHandle]:
        return list(self._providers.values())

    def provider_items(self) -> list[tuple[str, ProviderRuntimeHandle]]:
        return list(self._providers.items())

    def bindings_for(self, participant_name: str) -> ParticipantBindingSet:
        return self._bindings_by_participant.get(
            participant_name,
            ParticipantBindingSet(participant_name=participant_name, requires=()),
        )

    def _select_provider(
        self,
        export_name: str,
        request: ProviderRequest | None,
    ) -> _ExportProvider | None:
        provider = self._exports.provider_for(export_name)
        if provider is None:
            return None
        if request is not None and request.provider and provider.provider_name != request.provider:
            return None
        if request is not None and request.source:
            select_source = getattr(provider.provider, "request_source", None)
            if callable(select_source):
                owner = f"manifest:{provider.provider_name}:{export_name}"
                selected = bool(select_source(owner, request.source))
                if not selected:
                    return None
        return provider


class PluginParticipationFacts:
    """Expose plugin/provider binding facts through the canonical runtime seam."""

    def __init__(self) -> None:
        self._store = _PluginBindingStore(_ExportRegistry())
        self.controls = _BoundProviderControls(self)

    def register_provider(
        self,
        provider_name: str,
        provider: object,
        exports: tuple[str, ...],
    ) -> ProviderRuntimeHandle:
        return self._store.register_provider(provider_name, provider, exports)

    def bind_participant(
        self,
        participant_name: str,
        requires: tuple[str, ...],
        provider_requests=(),
    ) -> ParticipantBindingSet:
        return self._store.bind_participant(participant_name, requires, provider_requests)

    def provider(self, provider_name: str) -> ProviderRuntimeHandle | None:
        return self._store.provider(provider_name)

    def providers(self) -> list[ProviderRuntimeHandle]:
        return self._store.providers()

    def provider_items(self) -> list[tuple[str, ProviderRuntimeHandle]]:
        return self._store.provider_items()

    def bindings_for(self, participant_name: str) -> ParticipantBindingSet:
        return self._store.bindings_for(participant_name)

    def exports_for(
        self,
        participant_name: str,
        requires: tuple[str, ...],
    ) -> ParticipantExports:
        """Return a resolved export view scoped to one participant."""
        return ParticipantExports(self, participant_name, requires)
