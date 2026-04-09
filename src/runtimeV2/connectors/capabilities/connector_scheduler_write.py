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

"""Connector-owned scheduling policy above the runtime scheduler."""

from __future__ import annotations

from runtimeV2.connectors.capabilities.connector_game_detector_write import ConnectorGameDetectorWrite
from runtimeV2.connectors.capabilities.connector_read import ConnectorRead
from runtimeV2.connectors.plugin_handoff import ConnectorGameStateHookDispatcher
from runtimeV2.connectors.poller import ConnectorServicePoller
from runtimeV2.scheduler.capabilities.scheduler_write import SchedulerWrite


class ConnectorSchedulerWrite:
    """Switch connector jobs between probe mode and live polling."""

    PROBE_INTERVAL_MS = 5000

    def __init__(
        self,
        connector_read: ConnectorRead,
        scheduler_write: SchedulerWrite,
        poller: ConnectorServicePoller,
        game_detector_write: ConnectorGameDetectorWrite,
        plugin_handoff: ConnectorGameStateHookDispatcher | None = None,
        *,
        live_interval_ms: int,
    ) -> None:
        self._connector_read = connector_read
        self._scheduler_write = scheduler_write
        self._poller = poller
        self._game_detector_write = game_detector_write
        self._plugin_handoff = plugin_handoff
        self._live_interval_ms = max(1, int(live_interval_ms))

    def register_connector(self, connector_id: str) -> None:
        """Register probe and live jobs for one connector."""

        self._scheduler_write.register_job(
            job_id=self._probe_job_id(connector_id),
            owner_domain="connectors",
            interval_ms=self.PROBE_INTERVAL_MS,
            callback=lambda connector_id=connector_id: self._run_probe(connector_id),
            enabled=True,
        )
        self._scheduler_write.register_job(
            job_id=self._live_job_id(connector_id),
            owner_domain="connectors",
            interval_ms=self._live_interval_ms,
            callback=lambda connector_id=connector_id: self._run_live(connector_id),
            enabled=False,
        )

    def sync_scheduler_mode(self, connector_id: str) -> None:
        """Sync one connector between probe and live jobs."""

        active_source = self._connector_read.active_source(connector_id) or "none"
        if active_source not in {"none", "mock"}:
            self.enable_live_mode(connector_id)
            return
        self.enable_probe_mode(connector_id)

    def enable_probe_mode(self, connector_id: str) -> None:
        """Enable probe polling and disable live polling for one connector."""

        self._scheduler_write.set_enabled(self._probe_job_id(connector_id), True)
        self._scheduler_write.set_enabled(self._live_job_id(connector_id), False)

    def enable_live_mode(self, connector_id: str) -> None:
        """Enable live polling and disable probe polling for one connector."""

        self._scheduler_write.set_enabled(self._probe_job_id(connector_id), False)
        self._scheduler_write.set_enabled(self._live_job_id(connector_id), True)

    def _run_probe(self, connector_id: str) -> None:
        detected = self._game_detector_write.sync(connector_id)
        if detected is None:
            self.sync_scheduler_mode(connector_id)
            return
        self._poller.update_one(connector_id)
        self._sync_plugin_handoff(connector_id)
        self.sync_scheduler_mode(connector_id)

    def _run_live(self, connector_id: str) -> None:
        self._poller.update_one(connector_id)
        self._sync_plugin_handoff(connector_id)
        self.sync_scheduler_mode(connector_id)

    def sync_plugin_handoff(self, connector_id: str) -> bool:
        """Publish the current connector game state into the manifest-declared plugin hook."""

        return self._sync_plugin_handoff(connector_id)

    def _sync_plugin_handoff(self, connector_id: str) -> bool:
        if self._plugin_handoff is None:
            return False
        return self._plugin_handoff.sync_connector(connector_id)

    @staticmethod
    def _probe_job_id(connector_id: str) -> str:
        return f"connectors.{connector_id}.probe_game_state"

    @staticmethod
    def _live_job_id(connector_id: str) -> str:
        return f"connectors.{connector_id}.live_poll"
