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


# ---------------------------------------------------------------------------


@dataclass
class WidgetState:
    text:         str
    color:        str
    visible:      bool   # whole widget on/off (e.g. session inactive)
    text_visible: bool   # value text on/off (flash effect)
    label:        str

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, WidgetState):
            return False
        return (self.text == other.text
                and self.color == other.color
                and self.visible == other.visible
                and self.text_visible == other.text_visible)


# ---------------------------------------------------------------------------


class ConnectorUpdater:
    """Calls connector.update() once per tick for every registered connector.

    Register this as the FIRST Tickable in the PollLoop so that all runners
    see a fresh frame on every cycle.
    """

    def __init__(self, connectors: ConnectorRegistry) -> None:
        self._connectors = connectors

    def tick(self) -> None:
        for connector in self._connectors.all():
            try:
                connector.update()
            except Exception:
                pass


# ---------------------------------------------------------------------------


class TextWidgetRunner:
    """Reads one telemetry value per tick and emits a WidgetState when it changes.

    Implements Tickable — register with PollLoop after ConnectorUpdater.
    """

    def __init__(
        self,
        spec:        WidgetSpec,
        connectors:  ConnectorRegistry,
        plugin_name: str,
        on_update:   Callable[[WidgetState], None],
    ) -> None:
        self._spec        = spec
        self._connectors  = connectors
        self._plugin_name = plugin_name
        self._on_update   = on_update
        self._flash       = FlashState() if spec.flash_below is not None else None
        self._last:       WidgetState | None = None

    def tick(self) -> None:
        connector = self._connectors.get(self._plugin_name)
        if connector is None:
            return

        try:
            raw   = _resolve(connector, self._spec.source)
            text  = self._spec.format.format(raw)
            color = evaluate(self._spec.thresholds, raw) or _FALLBACK_COLOR

            flash_below = self._spec.flash_below
            if flash_below is not None and raw <= flash_below:
                if self._flash is None:
                    self._flash = FlashState()
                self._flash.tick()
                text_visible = self._flash.visible
            else:
                if self._flash is not None:
                    self._flash.reset()
                text_visible = True

            state = WidgetState(text=text, color=color, visible=True,
                                text_visible=text_visible, label=self._spec.label)
            if state != self._last:
                self._last = state
                _log.widget("state change", id=self._spec.id,
                            raw=round(raw, 3), text=text, color=color,
                            text_visible=text_visible)
                self._on_update(state)

        except Exception as exc:
            _log.warning("tick error for %r: %s", self._spec.id, exc)
