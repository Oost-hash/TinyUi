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

"""Capability registration for runtime V2 connectors."""

from __future__ import annotations

from dataclasses import dataclass

from runtimeV2.connectors.capabilities.connector_game_detector_read import ConnectorGameDetectorRead
from runtimeV2.connectors.capabilities.connector_game_detector_write import ConnectorGameDetectorWrite
from runtimeV2.connectors.capabilities.connector_scheduler_write import ConnectorSchedulerWrite
from runtimeV2.connectors.decision_store import ConnectorGameStateDecisionStore
from runtimeV2.connectors.game_detector import ConnectorGameDetector, validate_connector_detection_declarations
from runtimeV2.connectors.game_detector_store import ConnectorGameDetectorStore
from runtimeV2.contracts import EventBus
from runtimeV2.connectors.capabilities.connector_read import ConnectorRead
from runtimeV2.connectors.plugin_handoff import ConnectorGameStateHookDispatcher
from runtimeV2.connectors.capabilities.connector_write import ConnectorWrite
from runtimeV2.connectors.schemas.manifest import ConnectorManifest
from runtimeV2.connectors.poller import ConnectorServicePoller
from runtimeV2.connectors.service_registry import ConnectorServiceRegistry
from runtimeV2.contracts.widgets import WidgetVisibilityWriter
from runtimeV2.widgets.capabilities.widget_manual_override import WidgetManualOverride
from runtimeV2.scheduler.capabilities.scheduler_clock_write import SchedulerClockWrite
from runtimeV2.scheduler.capabilities.scheduler_write import SchedulerWrite


@dataclass(frozen=True)
class ConnectorCapabilities:
    """Capabilities exposed by the connectors domain."""

    read: ConnectorRead
    write: ConnectorWrite
    game_detector_read: ConnectorGameDetectorRead
    game_detector_write: ConnectorGameDetectorWrite
    scheduler_write: ConnectorSchedulerWrite


def register_connector_capabilities(
    declarations: dict[str, ConnectorManifest],
    registry: ConnectorServiceRegistry,
    poller: ConnectorServicePoller,
    scheduler_write: SchedulerWrite,
    scheduler_clock_write: SchedulerClockWrite,
    live_interval_ms: int,
    events: EventBus | None = None,
    widget_visibility_write: WidgetVisibilityWriter | None = None,
    widget_manual_override: WidgetManualOverride | None = None,
) -> ConnectorCapabilities:
    """Create connector domain capabilities."""

    validate_connector_detection_declarations(declarations)
    decision_store = ConnectorGameStateDecisionStore()
    detector_store = ConnectorGameDetectorStore()
    game_detector_write = ConnectorGameDetectorWrite(
        ConnectorGameDetector(declarations, detector_store, events),
    )
    connector_read = ConnectorRead(registry, decision_store, detector_store)
    connector_scheduler_write = ConnectorSchedulerWrite(
        connector_read,
        scheduler_write,
        scheduler_clock_write,
        poller,
        game_detector_write,
        ConnectorGameStateHookDispatcher(
            declarations,
            connector_read,
            decision_store,
            widget_visibility_write,
            widget_manual_override,
        ),
        live_interval_ms=live_interval_ms,
    )
    return ConnectorCapabilities(
        read=connector_read,
        write=ConnectorWrite(registry, poller, events, connector_scheduler_write),
        game_detector_read=ConnectorGameDetectorRead(detector_store),
        game_detector_write=game_detector_write,
        scheduler_write=connector_scheduler_write,
    )
