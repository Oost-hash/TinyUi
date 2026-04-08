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

"""Runtime V2 prototype orchestrator."""

from __future__ import annotations

from typing import TypeVar

from runtime_schema import DomainStatusChangedData, EventType, StartupResult, startup_error, startup_ok
from runtimeV2.domains import DomainRecord, DomainRegistration, DomainStartup, DomainStatus

T = TypeVar("T")


class RuntimeV2:
    """Small runtime V2 orchestrator prototype.

    This class intentionally does not replace the active Runtime yet. It is a
    visible sketch of the v0.5.5 direction: runtime owns orchestration and
    registries, while domains own their own startup and capabilities.
    """

    def __init__(self) -> None:
        self._domains: dict[str, DomainRegistration] = {}
        self._domain_records: dict[str, DomainRecord] = {}
        self._domain_results: dict[str, object] = {}
        self._capabilities: dict[str, object] = {}

    def register_domain(
        self,
        name: str,
        startup: DomainStartup,
        *,
        description: str = "",
    ) -> None:
        """Register a domain with the runtime orchestrator."""

        self._domains[name] = DomainRegistration(
            name=name,
            startup=startup,
            description=description,
        )
        self._set_domain_status(name, DomainStatus.REGISTERED)

    def domain_names(self) -> list[str]:
        """Return registered domain names in registration order."""

        return list(self._domains)

    def domain_records(self) -> list[DomainRecord]:
        """Return domain records in registration order."""

        return [self._domain_records[name] for name in self._domains]

    def domain_status(self, name: str) -> DomainStatus:
        """Return the current status for a registered domain."""

        return self._domain_records[name].status

    def start_registered_domains(self) -> StartupResult:
        """Start registered domains in registration order."""

        for registration in self._domains.values():
            result = self.start_domain(registration.name)
            if not result.ok:
                return result
        return startup_ok()

    def start_domain(self, name: str) -> StartupResult:
        """Start one registered domain."""

        registration = self._domains.get(name)
        if registration is None:
            return startup_error(f"Runtime V2 domain is not registered: {name}")

        self._set_domain_status(name, DomainStatus.STARTING)
        result = registration.startup(self)
        if result.ok:
            self._set_domain_status(name, DomainStatus.READY)
            return result

        error_message = result.error_message or f"Runtime V2 domain failed: {name}"
        self._set_domain_status(name, DomainStatus.ERROR, error_message=error_message)
        return startup_error(error_message)

    def register_domain_result(self, name: str, result: object) -> None:
        """Store the startup result owned by a domain."""

        if name not in self._domains:
            raise KeyError(f"Runtime V2 domain is not registered: {name}")
        self._domain_results[name] = result

    def domain_result(self, name: str, result_type: type[T]) -> T:
        """Return a typed domain result."""

        result = self._domain_results.get(name)
        if not isinstance(result, result_type):
            raise KeyError(f"Domain result '{name}' is not available as {result_type.__name__}")
        return result

    def register_capability(self, name: str, capability: object) -> None:
        """Register a capability exposed by runtime or one of its domains."""

        self._capabilities[name] = capability

    def capability(self, name: str, capability_type: type[T]) -> T:
        """Return a typed capability."""

        capability = self._capabilities.get(name)
        if not isinstance(capability, capability_type):
            raise KeyError(f"Capability '{name}' is not available as {capability_type.__name__}")
        return capability

    def _set_domain_status(
        self,
        name: str,
        status: DomainStatus,
        *,
        error_message: str = "",
    ) -> None:
        description = self._domains.get(name, DomainRegistration(name=name, startup=_missing_startup)).description
        self._domain_records[name] = DomainRecord(
            name=name,
            description=description,
            status=status,
            error_message=error_message,
        )
        self._emit_domain_status(name, status, error_message=error_message)

    def _emit_domain_status(
        self,
        name: str,
        status: DomainStatus,
        *,
        error_message: str = "",
    ) -> None:
        event_type = _event_type_for_domain_status(status)
        if event_type is None:
            return

        try:
            from runtimeV2.events.startup import EventsStartupResult

            events = self.domain_result("events", EventsStartupResult)
        except KeyError:
            return

        events.bus.emit_typed(
            event_type,
            DomainStatusChangedData(
                domain=name,
                status=status.value,
                error_message=error_message,
            ),
            source="runtimeV2",
        )


def _missing_startup(_runtime: RuntimeV2) -> StartupResult:
    return startup_error("Missing runtime V2 domain startup")


def _event_type_for_domain_status(status: DomainStatus) -> EventType | None:
    if status == DomainStatus.REGISTERED:
        return EventType.DOMAIN_REGISTERED
    if status == DomainStatus.STARTING:
        return EventType.DOMAIN_STARTING
    if status == DomainStatus.READY:
        return EventType.DOMAIN_READY
    if status == DomainStatus.ERROR:
        return EventType.DOMAIN_ERROR
    if status == DomainStatus.STOPPED:
        return EventType.DOMAIN_STOPPED
    return None
