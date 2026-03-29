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

"""Runtime-owned service for live plugin participation."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .participants import PluginParticipant

if TYPE_CHECKING:
    from tinyplugins.protocol import Plugin
    from tinycore.services import HostServices, RuntimeServices


class PluginParticipationRuntime:
    """Hold live plugin participants and drive their runtime phases."""

    def __init__(self):
        self._participants: list[PluginParticipant] = []

    def add_participant(self, participant: PluginParticipant) -> None:
        self._participants.append(participant)

    def register_participants(self, host: HostServices, runtime: RuntimeServices) -> None:
        from tinyplugins.context import PluginContext

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

    def participant_plugin(self, name: str) -> Plugin:
        for participant in self._participants:
            if participant.name == name:
                return participant.plugin
        raise KeyError(f"Plugin '{name}' not registered")

    @property
    def registered_participants(self) -> list[PluginParticipant]:
        return list(self._participants)
