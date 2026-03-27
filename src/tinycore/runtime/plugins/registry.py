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

"""Runtime-owned registry for live consumer plugin participants."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .consumer import ConsumerPluginParticipant

if TYPE_CHECKING:
    from tinycore.services import HostServices, RuntimeServices
    from tinycore.plugin.protocol import Plugin


class PluginRuntimeRegistry:
    """Stores live consumer participants and orchestrates two-phase init."""

    def __init__(self):
        self._participants: list[ConsumerPluginParticipant] = []

    def add(self, participant: ConsumerPluginParticipant) -> None:
        """Add one live consumer plugin participant to the runtime registry."""
        self._participants.append(participant)

    def register_all(self, host: HostServices, runtime: RuntimeServices) -> None:
        """Phase 1: call register() on all plugins with a scoped PluginContext."""
        from tinycore.plugin.context import PluginContext

        for participant in self._participants:
            participant.plugin.register(
                PluginContext(
                    host.persistence,
                    host.editors,
                    runtime.plugin_facts,
                    participant.name,
                    participant.requires,
                )
            )

    def start_all(self) -> None:
        """Phase 2: call start() on all plugins in order."""
        for participant in self._participants:
            participant.plugin.start()

    def stop_all(self) -> None:
        """Teardown: call stop() on all plugins in reverse order."""
        for participant in reversed(self._participants):
            participant.plugin.stop()

    def get(self, name: str) -> Plugin:
        """Return the registered live plugin participant with the given name."""
        for participant in self._participants:
            if participant.name == name:
                return participant.plugin
        raise KeyError(f"Plugin '{name}' not registered")

    @property
    def participants(self) -> list[ConsumerPluginParticipant]:
        return list(self._participants)

    @property
    def plugins(self) -> list[Plugin]:
        return [participant.plugin for participant in self._participants]


PluginRegistry = PluginRuntimeRegistry
RegisteredPlugin = ConsumerPluginParticipant
