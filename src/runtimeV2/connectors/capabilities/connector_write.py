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

"""Connector write capability for runtime V2."""

from __future__ import annotations

from runtimeV2.connectors.poller import ConnectorServicePoller
from runtimeV2.connectors.service_registry import ConnectorServiceRegistry


class ConnectorWrite:
    """Control connector service sources and updates."""

    def __init__(self, registry: ConnectorServiceRegistry, poller: ConnectorServicePoller) -> None:
        self._registry = registry
        self._poller = poller

    def request_source(self, connector_id: str, owner: str, source_name: str) -> bool:
        """Request a connector source."""

        return self._registry.request_source(connector_id, owner, source_name)

    def release_source(self, connector_id: str, owner: str) -> bool:
        """Release a connector source claim."""

        return self._registry.release_source(connector_id, owner)

    def update(self, connector_id: str) -> bool:
        """Update one connector service."""

        return self._poller.update_one(connector_id)

    def update_all(self) -> list[str]:
        """Update all connector services."""

        return self._poller.update_all()
