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
"""StateMonitorViewModel — live source inspector for Dev Tools.

Supports two kinds of inspectable sources:
  - ConnectorSource  : polls dot-path attributes on a telemetry connector
  - QObjectSource    : reads all Qt-registered properties via QMetaObject

The UI shows a selector strip; picking a source refreshes the property table
below it at 200 ms.  Change detection per key drives the flash/heartbeat dot.
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

from PySide6.QtCore import Property, QObject, QTimer, Signal, Slot

from tinycore.log import get_logger

if TYPE_CHECKING:
    from tinycore.telemetry.registry import ConnectorRegistry

_log = get_logger(__name__)

# Properties inherited from QObject base that add noise; skip them.
_SKIP_PROPS = frozenset({"objectName"})


# ── Source types ──────────────────────────────────────────────────────────────

class _Source:
    def __init__(self, label: str) -> None:
        self.label = label

    def snapshot(self) -> list[tuple[str, str]]:
        raise NotImplementedError


class _ConnectorSource(_Source):
    """Reads dot-path attributes from a telemetry connector."""

    def __init__(self, label: str, connector, paths: list[str]) -> None:
        super().__init__(label)
        self._connector = connector
        self._paths     = paths

    def snapshot(self) -> list[tuple[str, str]]:
        return [(path, self._read(path)) for path in self._paths]

    def _read(self, path: str) -> str:
        try:
            parts = path.split(".")
            obj   = self._connector
            for part in parts[:-1]:
                obj = getattr(obj, part)
            val = getattr(obj, parts[-1])()
            try:
                return f"{float(val):.6g}"
            except (ValueError, TypeError):
                return str(val)
        except Exception as exc:
            return f"err: {exc}"


class _QObjectSource(_Source):
    """Reads all Qt-registered properties from a QObject via QMetaObject."""

    def __init__(self, label: str, obj: QObject) -> None:
        super().__init__(label)
        self._obj = obj

    def snapshot(self) -> list[tuple[str, str]]:
        meta   = self._obj.metaObject()
        result = []
        for i in range(meta.propertyCount()):
            prop = meta.property(i)
            name = prop.name()
            if name in _SKIP_PROPS:
                continue
            try:
                val = prop.read(self._obj)
                if isinstance(val, list):
                    result.append((name, f"[{len(val)} items]"))
                elif isinstance(val, dict):
                    result.append((name, "{…}"))
                else:
                    try:
                        result.append((name, f"{float(val):.6g}"))
                    except (ValueError, TypeError):
                        result.append((name, str(val)))
            except Exception as exc:
                result.append((name, f"err: {exc}"))
        return result


# ── ViewModel ─────────────────────────────────────────────────────────────────

class StateMonitorViewModel(QObject):
    """Exposes a selectable set of live sources to QML.

    Usage::

        vm = StateMonitorViewModel()
        vm.setup(connectors, [("demo", "vehicle.fuel"), ...])
        vm.register_object("Widget: Fuel", fuel_ctx)
        # pass vm via extra_context; call vm.start() in pre_run
    """

    sourcesChanged  = Signal()
    selectedChanged = Signal()
    entriesChanged  = Signal()

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._sources:    list[_Source]  = []
        self._selected:   int            = -1
        self._prev:       dict[str, str] = {}
        self._changed_at: dict[str, int] = {}
        self._entries:    list[dict]     = []
        self._timer = QTimer(self)
        self._timer.setInterval(200)
        self._timer.timeout.connect(self._refresh)

    # ── Registration ──────────────────────────────────────────────────────────

    def register_object(self, label: str, obj: QObject) -> None:
        """Register a QObject for live property inspection."""
        self._sources.append(_QObjectSource(label, obj))
        if self._selected < 0:
            self._selected = 0
        self.sourcesChanged.emit()

    def setup(self, connectors: ConnectorRegistry,
              sources: list[tuple[str, str]]) -> None:
        """Register connector dot-path sources, grouped by plugin."""
        by_plugin: dict[str, list[str]] = {}
        for plugin_name, path in sources:
            by_plugin.setdefault(plugin_name, []).append(path)

        for plugin_name, paths in by_plugin.items():
            connector = connectors.get(plugin_name)
            if connector is not None:
                label = f"Connector: {plugin_name}"
                self._sources.append(_ConnectorSource(label, connector, paths))

        if self._selected < 0 and self._sources:
            self._selected = 0
        self.sourcesChanged.emit()
        _log.info("state monitor setup: %d sources", len(self._sources))

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    def start(self) -> None:
        """Start polling.  Must be called after QApplication is created."""
        self._timer.start()

    def shutdown(self) -> None:
        self._timer.stop()

    # ── Internal ──────────────────────────────────────────────────────────────

    def _refresh(self) -> None:
        if not self._sources or self._selected < 0:
            return

        snapshot    = self._sources[self._selected].snapshot()
        entries     = []
        changed_any = False
        now_ms      = int(time.time() * 1000)

        for key, value in snapshot:
            changed = value != self._prev.get(key)
            if changed:
                changed_any           = True
                self._prev[key]       = value
                self._changed_at[key] = now_ms

            entries.append({
                "key":       key,
                "value":     value,
                "changed":   changed,
                "changedAt": self._changed_at.get(key, 0),
            })

        self._entries = entries
        if changed_any:
            self.entriesChanged.emit()

    # ── QML properties ────────────────────────────────────────────────────────

    @Property("QVariantList", notify=sourcesChanged)
    def sources(self) -> list:
        """List of ``{label, index}`` for the source selector."""
        return [{"label": s.label, "index": i}
                for i, s in enumerate(self._sources)]

    @Property(int, notify=selectedChanged)
    def selectedIndex(self) -> int:
        return self._selected

    @Slot(int)
    def selectSource(self, index: int) -> None:
        if 0 <= index < len(self._sources) and index != self._selected:
            self._selected = index
            # Reset change tracking so the new source starts clean
            self._prev.clear()
            self._changed_at.clear()
            self._entries = []
            self.selectedChanged.emit()
            self.entriesChanged.emit()

    @Property("QVariantList", notify=entriesChanged)
    def entries(self) -> list:
        return self._entries
