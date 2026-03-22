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
"""PluginLifecycleManager — on-demand plugin start/stop with grace period.

When the user switches plugins, the new plugin starts immediately.
The old plugin keeps running for `grace_seconds` (default 30) in case
the user switches back — avoiding a full process restart on every click.
"""

from __future__ import annotations

import logging
import threading
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tinycore.plugin.registry import PluginRegistry

log = logging.getLogger(__name__)


class PluginLifecycleManager:
    """Manages plugin start/stop with a configurable grace period.

    Usage:
        lifecycle = PluginLifecycleManager(core.plugins)
        lifecycle.activate(core.plugins.plugins[0].name)   # start first plugin

        # on switch:
        lifecycle.activate("demo2")   # starts demo2, schedules demo stop after 30s

        # on shutdown:
        lifecycle.shutdown()
    """

    def __init__(self, registry: PluginRegistry, grace_seconds: float = 30.0) -> None:
        self._registry      = registry
        self._grace         = grace_seconds
        self._active:       str | None           = None
        self._running:      set[str]             = set()
        self._pending:      dict[str, threading.Timer] = {}

    # ── Public API ────────────────────────────────────────────────────────

    def activate(self, plugin_name: str) -> None:
        """Switch to a plugin.

        - Starts the plugin immediately if not already running.
        - Schedules the previously active plugin to stop after the grace period.
        - Cancels any pending stop if the plugin was already scheduled to stop.
        """
        if plugin_name == self._active:
            return

        log.debug("Activating plugin '%s' (was '%s')", plugin_name, self._active)

        # Cancel pending stop if this plugin was cooling down
        self._cancel_pending_stop(plugin_name)

        # Start if not already running
        if plugin_name not in self._running:
            self._start(plugin_name)

        # Schedule stop for the old active plugin
        old = self._active
        if old and old in self._running:
            self._schedule_stop(old)

        self._active = plugin_name

    def shutdown(self) -> None:
        """Cancel all pending timers and stop all running plugins cleanly."""
        for timer in list(self._pending.values()):
            timer.cancel()
        self._pending.clear()

        for name in list(self._running):
            self._stop(name)

    # ── Internal ──────────────────────────────────────────────────────────

    def _start(self, name: str) -> None:
        plugin = self._registry.get(name)
        log.info("Starting plugin '%s'", name)
        plugin.start()
        self._running.add(name)

    def _stop(self, name: str) -> None:
        plugin = self._registry.get(name)
        log.info("Stopping plugin '%s'", name)
        plugin.stop()
        self._running.discard(name)

    def _schedule_stop(self, name: str) -> None:
        if name in self._pending:
            return   # already scheduled
        log.debug("Scheduling stop for plugin '%s' in %.0fs", name, self._grace)
        timer = threading.Timer(self._grace, self._on_timer, args=(name,))
        timer.daemon = True
        self._pending[name] = timer
        timer.start()

    def _cancel_pending_stop(self, name: str) -> None:
        timer = self._pending.pop(name, None)
        if timer:
            log.debug("Cancelled scheduled stop for plugin '%s'", name)
            timer.cancel()

    def _on_timer(self, name: str) -> None:
        self._pending.pop(name, None)
        if name in self._running and name != self._active:
            self._stop(name)
