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

"""Runtime-owned warm activation for consumer plugin participation."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from tinycore.runtime.unit_ids import plugin_consumer_unit_id

if TYPE_CHECKING:
    from tinycore.runtime.models import RuntimeState
    from tinycore.runtime.plugins.registry import PluginRegistry
    from tinycore.runtime.provider_activity import ProviderActivity
    from tinycore.runtime.registry import RuntimeRegistry
    from tinycore.runtime.scheduler import RuntimeScheduler, ScheduledTaskHandle

log = logging.getLogger(__name__)


class PluginLifecycleManager:
    """Manages runtime-owned consumer activation with a configurable grace period."""

    def __init__(
        self,
        registry: PluginRegistry,
        *,
        scheduler: RuntimeScheduler,
        grace_seconds: float = 30.0,
    ) -> None:
        self._registry = registry
        self._scheduler = scheduler
        self._grace = grace_seconds
        self._active: str | None = None
        self._running: set[str] = set()
        self._pending: dict[str, ScheduledTaskHandle] = {}
        self._runtime_registry: RuntimeRegistry | None = None
        self._provider_activity: ProviderActivity | None = None

    def activate(self, plugin_name: str) -> None:
        """Switch to a plugin participant and keep the old one warm briefly."""
        if plugin_name == self._active:
            return
        log.debug("Activating plugin '%s' (was '%s')", plugin_name, self._active)
        self._cancel_pending_stop(plugin_name)
        if plugin_name not in self._running:
            self._start(plugin_name)
        old = self._active
        if old and old in self._running:
            self._schedule_stop(old)
        self._active = plugin_name

    def shutdown(self) -> None:
        """Cancel all pending timers and stop all running plugin participants."""
        for task_id in [self._task_id(name) for name in self._pending]:
            self._scheduler.cancel(task_id)
        self._pending.clear()
        for name in list(self._running):
            self._stop(name)

    def attach_runtime_registry(self, registry: RuntimeRegistry) -> None:
        """Attach runtime unit tracking for plugin consumer lifecycle units."""
        self._runtime_registry = registry
        for name in self._running:
            unit_id = plugin_consumer_unit_id(name)
            if registry.get(unit_id) is not None:
                registry.set_state(unit_id, "running")

    def attach_provider_activity(self, provider_activity: ProviderActivity) -> None:
        """Attach runtime-owned provider activity so consumer heat drives providers."""
        self._provider_activity = provider_activity
        for name in self._running:
            provider_activity.activate_consumer(name)

    def active_consumer_names(self) -> tuple[str, ...]:
        """Return the currently active or warm-running consumer names."""
        return tuple(sorted(self._running))

    @property
    def grace_period_ms(self) -> int:
        """Return the warm shutdown grace period in milliseconds."""
        return int(self._grace * 1000)

    def _start(self, name: str) -> None:
        plugin = self._registry.get(name)
        log.info("Starting plugin '%s'", name)
        self._set_runtime_state(name, "starting")
        plugin.start()
        self._running.add(name)
        if self._provider_activity is not None:
            self._provider_activity.activate_consumer(name)
        self._set_runtime_state(name, "running")

    def _stop(self, name: str) -> None:
        plugin = self._registry.get(name)
        log.info("Stopping plugin '%s'", name)
        self._set_runtime_state(name, "stopping")
        plugin.stop()
        self._running.discard(name)
        if self._provider_activity is not None:
            self._provider_activity.deactivate_consumer(name)
        self._set_runtime_state(name, "stopped")

    def _schedule_stop(self, name: str) -> None:
        if name in self._pending:
            return
        log.debug("Scheduling stop for plugin '%s' in %.0fs", name, self._grace)
        task_id = self._task_id(name)
        handle = self._scheduler.schedule_delay(
            task_id,
            delay_ms=self.grace_period_ms,
            callback=lambda name=name: self._on_timer(name),
        )
        self._pending[name] = handle

    def _cancel_pending_stop(self, name: str) -> None:
        handle = self._pending.pop(name, None)
        if handle:
            log.debug("Cancelled scheduled stop for plugin '%s'", name)
            self._scheduler.cancel(handle.task_id)

    def _on_timer(self, name: str) -> None:
        self._pending.pop(name, None)
        if name in self._running and name != self._active:
            self._stop(name)

    def _set_runtime_state(self, name: str, state: RuntimeState) -> None:
        if self._runtime_registry is None:
            return
        unit_id = plugin_consumer_unit_id(name)
        info = self._runtime_registry.get(unit_id)
        if info is None:
            return
        if info.activation_policy not in {"warm", "on_demand"}:
            raise RuntimeError(
                f"plugin consumer unit '{unit_id}' cannot change activation state; "
                f"activation policy is '{info.activation_policy}'"
            )
        self._runtime_registry.set_state(unit_id, state)

    def _task_id(self, name: str) -> str:
        return f"{plugin_consumer_unit_id(name)}:grace-stop"
