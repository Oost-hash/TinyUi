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
"""Widget runners — Tickable implementations driven by the PollLoop.

ProviderUpdater    — calls provider.update() once per tick for active runtimes.
TextWidgetRunner   — reads one telemetry value, evaluates threshold and flash.
"""

from __future__ import annotations

from dataclasses import dataclass
from numbers import Real
from typing import cast
from typing import Callable

from tinycore.logging import get_logger
from tinycore.session.runtime import SessionRuntime
from .flash import FlashState
from .fields import read_field
from .threshold import evaluate
from .spec import WidgetSpec

_FALLBACK_COLOR = "#E0E0E0"
_log = get_logger(__name__)


def _binding_for_widget(
    session: SessionRuntime,
    consumer_name: str,
    spec: WidgetSpec,
):
    """Resolve the provider binding used by a widget."""
    bindings = session.bindings_for(consumer_name)
    return bindings.require(spec.capability)


# ---------------------------------------------------------------------------


@dataclass
class WidgetState:
    text:         str
    color:        str
    visible:      bool   # whole widget on/off (e.g. session inactive)
    text_visible: bool   # value text on/off (flash effect)
    label:        str
    flash_target: str = "value"  # "value" | "text" | "widget"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, WidgetState):
            return False
        return (self.text         == other.text
                and self.color        == other.color
                and self.visible      == other.visible
                and self.text_visible == other.text_visible
                and self.flash_target == other.flash_target)


# ---------------------------------------------------------------------------


class ProviderUpdater:
    """Calls provider.update() once per tick for every active provider runtime.

    Also tracks active/paused state transitions per provider and logs them
    via the ``connector`` debug category.

    Register this as the FIRST Tickable in the PollLoop so that all runners
    see a fresh frame on every cycle.
    """

    def __init__(self, session: SessionRuntime) -> None:
        self._session = session
        # {provider_name: {"active": bool|None, "paused": bool|None}}
        self._prev: dict[str, dict[str, bool | None]] = {}

    def tick(self) -> None:
        errors = self._session.update_providers()
        for name, error in errors:
            _log.connector("update error", plugin=name, error=error)
        for name, handle in self._session.active_provider_items():
            self._check_state(name, handle.provider)

    def _check_state(self, name: str, provider) -> None:
        """Detect and log active/paused transitions for one provider runtime."""
        try:
            active = provider.state.active()
            paused = provider.state.paused()
        except Exception:
            return  # provider doesn't support state — skip

        prev = self._prev.get(name)
        if prev is None:
            # First observation — record without logging (no "previous" to compare)
            self._prev[name] = {"active": active, "paused": paused}
            return

        if active != prev["active"]:
            prev["active"] = active
            if active:
                _log.connector("game started", plugin=name)
            else:
                _log.connector("game stopped", plugin=name)

        if paused != prev["paused"]:
            prev["paused"] = paused
            if paused:
                _log.connector("game paused", plugin=name)
            else:
                _log.connector("game resumed", plugin=name)


# ---------------------------------------------------------------------------


class TextWidgetRunner:
    """Reads one telemetry value per tick and emits a WidgetState when it changes.

    Implements Tickable — register with PollLoop after ProviderUpdater.
    """

    def __init__(
        self,
        spec:          WidgetSpec,
        session:       SessionRuntime,
        consumer_name: str,
        on_update:     Callable[[WidgetState], None],
    ) -> None:
        self._spec = spec
        self._session = session
        self._consumer_name = consumer_name
        self._on_update = on_update
        self._flash = FlashState()
        self._last: WidgetState | None = None
        self._missing_logged = False

    @staticmethod
    def _provider_mode(provider) -> str:
        mode = getattr(provider, "mode", None)
        return str(mode()) if callable(mode) else "real"

    def tick(self) -> None:
        try:
            binding = _binding_for_widget(self._session, self._consumer_name, self._spec)
        except KeyError as exc:
            if not self._missing_logged:
                _log.warning(
                    "widget binding missing  consumer=%s  widget=%s  capability=%s  error=%s",
                    self._consumer_name,
                    self._spec.id,
                    self._spec.capability,
                    str(exc),
                )
                self._missing_logged = True
            return

        try:
            if self._provider_mode(binding.provider) == "inactive":
                self._flash.reset()
                state = WidgetState(
                    text="",
                    color=_FALLBACK_COLOR,
                    visible=False,
                    text_visible=True,
                    label=self._spec.label,
                    flash_target="value",
                )
                if state != self._last:
                    self._last = state
                    self._on_update(state)
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
                    (e for e in sorted(self._spec.thresholds, key=lambda e: e.value)
                     if raw_number is not None and raw_number <= e.value),
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

            state = WidgetState(text=text, color=color, visible=True,
                                text_visible=text_visible, label=self._spec.label,
                                flash_target=flash_target)
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
                self._on_update(state)

        except Exception as exc:
            _log.warning("tick error for %r: %s", self._spec.id, exc)
