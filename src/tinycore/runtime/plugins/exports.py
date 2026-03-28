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

"""Resolved runtime export contracts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .facts import PluginParticipationFacts


@dataclass(frozen=True)
class ExportBinding:
    """Resolved provider for one exported runtime surface."""

    export_name: str
    provider_name: str
    provider: object


class ParticipantExports:
    """Resolved export view scoped to one plugin participant."""

    def __init__(
        self,
        participation: PluginParticipationFacts,
        participant_name: str,
        required: tuple[str, ...],
    ) -> None:
        self._participation = participation
        self._participant_name = participant_name
        self._required = required

    def required(self) -> tuple[str, ...]:
        """Declared export requirements for this participant."""
        return self._required

    def all(self) -> dict[str, ExportBinding]:
        """All resolved export bindings currently known for this participant."""
        return dict(self._participation.bindings_for(self._participant_name).resolved)

    def get(self, export_name: str) -> ExportBinding | None:
        """Resolve an exported surface if it was declared by this participant."""
        if export_name not in self._required:
            raise KeyError(f"Export '{export_name}' was not declared in requires")
        return self._participation.bindings_for(self._participant_name).get(export_name)

    def require(self, export_name: str) -> ExportBinding:
        """Resolve a declared export or raise KeyError."""
        if export_name not in self._required:
            raise KeyError(f"Export '{export_name}' was not declared in requires")
        return self._participation.bindings_for(self._participant_name).require(export_name)
