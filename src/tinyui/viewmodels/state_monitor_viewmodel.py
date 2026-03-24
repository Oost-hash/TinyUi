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
"""StateMonitorViewModel — live connector state viewer for Dev Tools.

Polls all widget sources at 200 ms and only emits entriesChanged when at
least one value has changed since the previous cycle.  Each entry carries a
"changed" flag so QML can flash the affected rows.
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

from PySide6.QtCore import Property, QObject, QTimer, Signal

from tinycore.log import get_logger

if TYPE_CHECKING:
    from tinycore.telemetry.registry import ConnectorRegistry

_log = get_logger(__name__)


def _read(connector, path: str) -> str:
    """Resolve a dot-path against a connector and return a formatted string."""
    try:
        parts = path.split(".")
        obj = connector
        for part in parts[:-1]:
            obj = getattr(obj, part)
        val = getattr(obj, parts[-1])()
        try:
            return f"{float(val):.6g}"
        except (ValueError, TypeError):
            return str(val)
    except Exception as exc:
        return f"err: {exc}"


class StateMonitorViewModel(QObject):
    """Exposes live connector readings as a QVariantList for QML.

    Usage:
        vm = StateMonitorViewModel()
        vm.setup(connectors, [("demo", "vehicle.fuel"), ...])
        # pass vm to QML via extra_context
        vm.shutdown()   # call on aboutToQuit
    """

    entriesChanged = Signal()

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._connectors:  ConnectorRegistry | None = None
        self._sources:     list[tuple[str, str]]   = []
        self._prev:        dict[str, str]           = {}
        self._changed_at:  dict[str, int]           = {}  # ms timestamp of last change
        self._entries:     list[dict]               = []
        self._timer = QTimer(self)
        self._timer.setInterval(200)
        self._timer.timeout.connect(self._refresh)

    def setup(self, connectors: ConnectorRegistry,
              sources: list[tuple[str, str]]) -> None:
        """Start monitoring the given (plugin_name, source_path) pairs."""
        self._connectors = connectors
        self._sources    = sources
        self._timer.start()
        _log.debug("state monitor started, watching %d sources", len(sources))

    def shutdown(self) -> None:
        self._timer.stop()

    # ── Internal ──────────────────────────────────────────────────────────────

    def _refresh(self) -> None:
        if self._connectors is None:
            return

        entries:     list[dict] = []
        changed_any: bool       = False

        for plugin_name, path in self._sources:
            connector = self._connectors.get(plugin_name)
            key       = f"{plugin_name}.{path}"
            value     = _read(connector, path) if connector is not None else "—"
            changed   = value != self._prev.get(key)

            now_ms = int(time.time() * 1000)
            if changed:
                changed_any           = True
                self._prev[key]       = value
                self._changed_at[key] = now_ms

            entries.append({
                "key":        key,
                "value":      value,
                "changed":    changed,
                "changedAt":  self._changed_at.get(key, 0),
            })

        self._entries = entries
        if changed_any:
            self.entriesChanged.emit()

    # ── QML property ──────────────────────────────────────────────────────────

    @Property("QVariantList", notify=entriesChanged)
    def entries(self) -> list:
        return self._entries
