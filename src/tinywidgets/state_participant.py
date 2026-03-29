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

"""Widget state derivation participants driven by the runtime update loop."""

from __future__ import annotations

from dataclasses import dataclass
from numbers import Real
from typing import Callable, cast

from tinyruntime_schema import get_logger
from tinyruntime.plugins.facts import PluginParticipationFacts

from .fields import read_field
from .flash import FlashState
from .spec import WidgetSpec
from .threshold import evaluate

_FALLBACK_COLOR = "#E0E0E0"
_log = get_logger(__name__)


def _binding_for_widget(
    participation: PluginParticipationFacts,
    participant_name: str,
    spec: WidgetSpec,
):
    """Resolve the provider binding used by a widget state participant."""
    bindings = participation.bindings_for(participant_name)
    return bindings.require(spec.capability)


@dataclass
class WidgetDisplayState:
    text: str
    color: str
    visible: bool
    text_visible: bool
    label: str
    flash_target: str = "value"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, WidgetDisplayState):
            return False
        return (
            self.text == other.text
            and self.color == other.color
            and self.visible == other.visible
            and self.text_visible == other.text_visible
            and self.flash_target == other.flash_target
        )


class WidgetStateParticipant:
    """Derive one widget display state from refreshed runtime participation data."""

    def __init__(
        self,
        spec: WidgetSpec,
        participation: PluginParticipationFacts,
        participant_name: str,
        emit_state: Callable[[WidgetDisplayState], None],
    ) -> None:
        self._spec = spec
        self._participation = participation
        self._participant_name = participant_name
        self._emit_state = emit_state
        self._flash = FlashState()
        self._last: WidgetDisplayState | None = None
        self._missing_logged = False

    @staticmethod
    def _provider_mode(provider) -> str:
        mode = getattr(provider, "mode", None)
        return str(mode()) if callable(mode) else "real"

    def tick(self) -> None:
        try:
            binding = _binding_for_widget(
                self._participation,
                self._participant_name,
                self._spec,
            )
        except KeyError as exc:
            if not self._missing_logged:
                _log.warning(
                    "widget binding missing  participant=%s  widget=%s  capability=%s  error=%s",
                    self._participant_name,
                    self._spec.id,
                    self._spec.capability,
                    str(exc),
                )
                self._missing_logged = True
            return

        try:
            if self._provider_mode(binding.provider) == "inactive":
                self._flash.reset()
                state = WidgetDisplayState(
                    text="",
                    color=_FALLBACK_COLOR,
                    visible=False,
                    text_visible=True,
                    label=self._spec.label,
                    flash_target="value",
                )
                if state != self._last:
                    self._last = state
                    self._emit_state(state)
                return

            raw_value = read_field(self._spec.capability, self._spec.field, binding.provider)
            is_numeric = isinstance(raw_value, Real) and not isinstance(raw_value, bool)
            raw_number = float(cast(Real, raw_value)) if is_numeric else None

            text = self._spec.format.format(raw_value)
            color = (
                evaluate(self._spec.thresholds, raw_number) or _FALLBACK_COLOR
                if raw_number is not None
                else _FALLBACK_COLOR
            )
            self._missing_logged = False

            active = (
                next(
                    (
                        entry
                        for entry in sorted(self._spec.thresholds, key=lambda entry: entry.value)
                        if raw_number is not None and raw_number <= entry.value
                    ),
                    None,
                )
                if raw_number is not None
                else None
            )
            flash_target = active.flash_target if active is not None else "value"
            if active is not None and active.flash:
                self._flash.interval = active.flash_speed
                self._flash.tick()
                text_visible = self._flash.visible
            else:
                self._flash.reset()
                text_visible = True

            state = WidgetDisplayState(
                text=text,
                color=color,
                visible=True,
                text_visible=text_visible,
                label=self._spec.label,
                flash_target=flash_target,
            )
            if state != self._last:
                self._last = state
                _log.widget(
                    "state change",
                    id=self._spec.id,
                    raw=round(raw_number, 3) if raw_number is not None else str(raw_value),
                    text=text,
                    color=color,
                    text_visible=text_visible,
                )
                self._emit_state(state)

        except Exception as exc:
            _log.warning("widget state derivation error for %r: %s", self._spec.id, exc)
