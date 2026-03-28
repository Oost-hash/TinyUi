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

"""Runtime-owned staged update driver for recurring host refresh and derivation."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Literal, Protocol, runtime_checkable

from .qt_timer import RuntimeQtTimer

UpdateStage = Literal["refresh", "derive"]
_UPDATE_STAGE_ORDER: tuple[UpdateStage, ...] = ("refresh", "derive")


@runtime_checkable
class UpdateParticipant(Protocol):
    """Anything that can participate in the staged runtime update cycle."""

    def tick(self) -> None: ...


@dataclass(frozen=True)
class UpdateParticipantInfo:
    """Declared update participant plus its assigned runtime stage."""

    label: str
    stage: UpdateStage


class RuntimeUpdateLoop:
    """Drive staged update participants at a fixed interval via a runtime-owned Qt timer."""

    def __init__(self, interval_ms: int = 100) -> None:
        self._participants_by_stage: dict[UpdateStage, list[tuple[str, UpdateParticipant]]] = {
            stage: [] for stage in _UPDATE_STAGE_ORDER
        }
        self._timer = RuntimeQtTimer(interval_ms=interval_ms, callback=self._tick)

    @property
    def interval_ms(self) -> int:
        return self._timer.interval_ms

    def register(
        self,
        participant: UpdateParticipant,
        *,
        label: str,
        stage: UpdateStage = "derive",
    ) -> None:
        """Register one update participant into an explicit runtime update stage."""
        if stage not in self._participants_by_stage:
            raise ValueError(f"Unknown runtime update stage '{stage}'")
        self._participants_by_stage[stage].append((label, participant))

    def register_refresh_participant(
        self,
        participant: UpdateParticipant,
        *,
        label: str,
    ) -> None:
        """Register one participant that refreshes runtime-backed state."""
        self.register(participant, label=label, stage="refresh")

    def register_derived_participant(
        self,
        participant: UpdateParticipant,
        *,
        label: str,
    ) -> None:
        """Register one participant that derives state from refreshed runtime data."""
        self.register(participant, label=label, stage="derive")

    def participant_infos(self) -> tuple[UpdateParticipantInfo, ...]:
        """Return registered update participants in stage order."""
        infos: list[UpdateParticipantInfo] = []
        for stage in _UPDATE_STAGE_ORDER:
            infos.extend(
                UpdateParticipantInfo(label=label, stage=stage)
                for label, _participant in self._participants_by_stage[stage]
            )
        return tuple(infos)

    def start(self) -> None:
        self._timer.start()

    def stop(self) -> None:
        self._timer.stop()

    def _tick(self) -> None:
        for participant in self._ordered_participants():
            participant.tick()

    def _ordered_participants(self) -> Iterable[UpdateParticipant]:
        for stage in _UPDATE_STAGE_ORDER:
            for _label, participant in self._participants_by_stage[stage]:
                yield participant
