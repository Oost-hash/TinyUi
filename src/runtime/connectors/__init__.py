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

"""Connector runtime helpers, policies, and registries."""

from runtime.connectors.contracts import ConnectorInspectionSnapshot, ConnectorServiceAccess
from runtime.connectors.policy import (
    register_connector_service,
    required_connector_ids,
    unregister_connector_service,
)
from runtime.connectors.service_loader import load_connector_service
from runtime.connectors.service_registry import ConnectorServiceRegistry, RegisteredConnectorService
from runtime.connectors.startup import startup_connectors, get_connectors_result, ConnectorsStartupResult

__all__ = [
    "ConnectorInspectionSnapshot",
    "ConnectorServiceAccess",
    "ConnectorServiceRegistry",
    "RegisteredConnectorService",
    "load_connector_service",
    "register_connector_service",
    "required_connector_ids",
    "unregister_connector_service",
    "startup_connectors",
    "get_connectors_result",
]
