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

"""Runtime-owned protocols for session-backed plugin participation seams."""

from __future__ import annotations

from typing import Protocol

from tinycore.session.control import DemoConfig
from tinycore.session.runtime import ConsumerBindingSet, ProviderHandle


class PluginParticipationControlsBackend(Protocol):
    """Minimal control surface needed by runtime-owned plugin participation."""

    def provider_name_for(self, consumer_name: str, capability: str) -> str: ...
    def supports_demo_mode(self, consumer_name: str, capability: str) -> bool: ...
    def request_demo_mode(self, consumer_name: str, capability: str, owner: str) -> bool: ...
    def release_demo_mode(self, consumer_name: str, capability: str, owner: str) -> bool: ...
    def provider_mode(self, consumer_name: str, capability: str) -> str: ...
    def active_game(self, consumer_name: str, capability: str) -> str: ...
    def demo_config(self, consumer_name: str, capability: str) -> DemoConfig: ...
    def set_demo_min(self, consumer_name: str, capability: str, value: float) -> bool: ...
    def set_demo_max(self, consumer_name: str, capability: str, value: float) -> bool: ...
    def set_demo_speed(self, consumer_name: str, capability: str, value: float) -> bool: ...


class PluginParticipationStore(Protocol):
    """Minimal session-backed store surface needed by runtime-owned plugin facts."""

    @property
    def controls(self) -> PluginParticipationControlsBackend: ...

    def register_provider(
        self,
        provider_name: str,
        provider: object,
        exports: tuple[str, ...],
    ) -> ProviderHandle: ...

    def bind_consumer(
        self,
        consumer_name: str,
        requires: tuple[str, ...],
        provider_requests=(),
    ) -> ConsumerBindingSet: ...

    def provider(self, provider_name: str) -> ProviderHandle | None: ...
    def providers(self) -> list[ProviderHandle]: ...
    def provider_items(self) -> list[tuple[str, ProviderHandle]]: ...
    def bindings_for(self, consumer_name: str) -> ConsumerBindingSet: ...
