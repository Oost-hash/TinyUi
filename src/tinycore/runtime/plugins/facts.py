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

"""Runtime-owned facts facade over session-backed plugin participation state."""

from __future__ import annotations

from tinycore.session.runtime import ConsumerBindingSet, ProviderHandle

from .controls import PluginParticipationControls
from .protocols import PluginParticipationStore

ConsumerParticipationBindings = ConsumerBindingSet
ProviderParticipationHandle = ProviderHandle


class PluginParticipationFacts:
    """Expose plugin/provider binding facts through a runtime-owned seam."""

    def __init__(self, session: PluginParticipationStore) -> None:
        self._session = session
        self.controls = PluginParticipationControls(session.controls)

    def register_provider(
        self,
        provider_name: str,
        provider: object,
        exports: tuple[str, ...],
    ) -> ProviderParticipationHandle:
        return self._session.register_provider(provider_name, provider, exports)

    def bind_consumer(
        self,
        consumer_name: str,
        requires: tuple[str, ...],
        provider_requests=(),
    ) -> ConsumerParticipationBindings:
        return self._session.bind_consumer(consumer_name, requires, provider_requests)

    def provider(self, provider_name: str) -> ProviderParticipationHandle | None:
        return self._session.provider(provider_name)

    def providers(self) -> list[ProviderParticipationHandle]:
        return self._session.providers()

    def provider_items(self) -> list[tuple[str, ProviderParticipationHandle]]:
        return self._session.provider_items()

    def bindings_for(self, consumer_name: str) -> ConsumerParticipationBindings:
        return self._session.bindings_for(consumer_name)
