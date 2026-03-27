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

"""Runtime-owned provider activation and update coordination."""

from __future__ import annotations

from tinycore.runtime.models import RuntimeState
from tinycore.runtime.unit_ids import provider_export_unit_id, provider_runtime_unit_id
from tinycore.runtime.plugins.facts import PluginParticipationFacts

from .registry import RuntimeRegistry


class ProviderActivity:
    """Own provider heat, activation state, and provider update routing."""

    def __init__(self, participation: PluginParticipationFacts) -> None:
        self._participation = participation
        self._active_participants: set[str] = set()
        self._active_provider_names: set[str] = set()
        self._runtime_registry: RuntimeRegistry | None = None

    def activate_participant(self, participant_name: str) -> None:
        self._active_participants.add(participant_name)
        self._refresh_active_providers()

    def deactivate_participant(self, participant_name: str) -> None:
        self._active_participants.discard(participant_name)
        self._refresh_active_providers()

    def active_provider_names(self) -> tuple[str, ...]:
        return tuple(sorted(self._active_provider_names))

    def active_provider_items(self):
        return [
            (provider_name, handle)
            for provider_name, handle in self._participation.provider_items()
            if provider_name in self._active_provider_names
        ]

    def attach_runtime_registry(self, registry: RuntimeRegistry) -> None:
        self._runtime_registry = registry
        self._sync_provider_runtime_states(set(), self._active_provider_names)

    def bindings_changed(self, participant_name: str) -> None:
        if participant_name in self._active_participants:
            self._refresh_active_providers()

    def provider_registered(self, provider_name: str) -> None:
        self._refresh_active_providers()
        if provider_name not in self._active_provider_names:
            self._set_provider_runtime_state(provider_name, "idle")

    def update_providers(self) -> list[tuple[str, str]]:
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

    def _refresh_active_providers(self) -> None:
        previous = set(self._active_provider_names)
        active: set[str] = set()
        for participant_name in self._active_participants:
            bindings = self._participation.bindings_for(participant_name)
            active.update(binding.provider_name for binding in bindings.resolved.values())
        self._active_provider_names = active
        self._sync_provider_runtime_states(previous, active)

    def _sync_provider_runtime_states(self, previous: set[str], current: set[str]) -> None:
        if self._runtime_registry is None:
            return
        for provider_name in previous - current:
            self._set_provider_runtime_state(provider_name, "idle")
        for provider_name in current:
            self._set_provider_runtime_state(provider_name, "running")

    def _set_provider_runtime_state(self, provider_name: str, state: RuntimeState) -> None:
        if self._runtime_registry is None:
            return
        handle = self._participation.provider(provider_name)
        runtime_unit_id = provider_runtime_unit_id(provider_name)
        if self._runtime_registry.get(runtime_unit_id) is not None:
            self._runtime_registry.set_state(runtime_unit_id, state)
        if handle is None:
            return
        for export_name in handle.exports:
            export_unit_id = provider_export_unit_id(provider_name, export_name)
            if self._runtime_registry.get(export_unit_id) is not None:
                self._runtime_registry.set_state(export_unit_id, state)
