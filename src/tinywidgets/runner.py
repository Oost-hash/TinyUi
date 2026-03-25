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

ConnectorUpdater   — calls connector.update() once per tick for all connectors.
TextWidgetRunner   — reads one telemetry value, evaluates threshold and flash.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable

from tinycore.log import get_logger
from tinycore.session.runtime import ConsumerBindingSet, SessionRuntime
from .flash import FlashState
from .threshold import evaluate
from .spec import WidgetSpec

if TYPE_CHECKING:
    from tinycore.telemetry.registry import ConnectorRegistry

_FALLBACK_COLOR = "#E0E0E0"
_log = get_logger(__name__)


def _resolve(connector, path: str) -> float:
    """Resolve a dot-path against a connector and call the final method.

    "vehicle.fuel"  →  connector.vehicle.fuel()
    """
    parts = path.split(".")
    obj = connector
    for part in parts[:-1]:
        obj = getattr(obj, part)
    return float(getattr(obj, parts[-1])())


def _binding_for_widget(
    session: SessionRuntime,
    consumer_name: str,
    spec: WidgetSpec,
):
    """Resolve the provider binding used by a widget."""
    bindings = session.bindings_for(consumer_name)
    if spec.capability:
        return bindings.get(spec.capability)

    if len(bindings.resolved) == 1:
        return next(iter(bindings.resolved.values()))

    return None


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


class ConnectorUpdater:
    """Calls connector.update() once per tick for every registered connector.

    Also tracks active/paused state transitions per connector and logs them
    via the ``connector`` debug category.

    Register this as the FIRST Tickable in the PollLoop so that all runners
    see a fresh frame on every cycle.
    """

    def __init__(self, connectors: ConnectorRegistry) -> None:
        self._connectors = connectors
        # {plugin_name: {"active": bool|None, "paused": bool|None}}
        self._prev: dict[str, dict[str, bool | None]] = {}

    def tick(self) -> None:
        for name, connector in self._connectors.items():
            try:
                connector.update()
                self._check_state(name, connector)
            except Exception as exc:
                _log.connector("update error", plugin=name, error=str(exc))

    def _check_state(self, name: str, connector) -> None:
        """Detect and log active/paused transitions for one connector."""
        try:
            active = connector.state.active()
            paused = connector.state.paused()
        except Exception:
            return  # connector doesn't support state — skip

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

    Implements Tickable — register with PollLoop after ConnectorUpdater.
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

    def tick(self) -> None:
        binding = _binding_for_widget(self._session, self._consumer_name, self._spec)
        if binding is None:
            if not self._missing_logged:
                target = self._spec.capability or "<implicit single binding>"
                _log.warning(
                    "widget binding missing  consumer=%s  widget=%s  capability=%s",
                    self._consumer_name,
                    self._spec.id,
                    target,
                )
                self._missing_logged = True
            return

        try:
            raw   = _resolve(binding.provider, self._spec.source)
            text  = self._spec.format.format(raw)
            color = evaluate(self._spec.thresholds, raw) or _FALLBACK_COLOR
            self._missing_logged = False

            active = next(
                (e for e in sorted(self._spec.thresholds, key=lambda e: e.value)
                 if raw <= e.value),
                None,
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
                _log.widget("state change", id=self._spec.id,
                            raw=round(raw, 3), text=text, color=color,
                            text_visible=text_visible)
                self._on_update(state)

        except Exception as exc:
            _log.warning("tick error for %r: %s", self._spec.id, exc)
