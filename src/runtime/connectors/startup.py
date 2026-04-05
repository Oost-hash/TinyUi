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

"""Connector domain startup."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from runtime.connectors.service_registry import ConnectorServiceRegistry

if TYPE_CHECKING:
    from runtime_schema import EventBus
    from runtime_schema.startup import StartupResult


@dataclass
class ConnectorsStartupResult:
    """Result of connectors domain startup."""

    registry: ConnectorServiceRegistry


# Module-level storage for startup result
_connectors_result: ConnectorsStartupResult | None = None


def startup_connectors(event_bus: EventBus | None = None) -> StartupResult:
    """Startup function for connector domain.
    
    Creates the connector service registry that will hold all active
    connector services during runtime.
    
    Returns:
        StartupResult with ok=True on success.
    """
    from runtime_schema.startup import startup_ok, startup_error
    global _connectors_result

    try:
        registry = ConnectorServiceRegistry()
        _connectors_result = ConnectorsStartupResult(registry=registry)
        return startup_ok()
    except Exception as e:
        _connectors_result = None
        return startup_error(f"Connector startup failed: {e}")


def get_connectors_result() -> ConnectorsStartupResult | None:
    """Get the connector startup result.
    
    Returns None if startup was not called or failed.
    """
    return _connectors_result
