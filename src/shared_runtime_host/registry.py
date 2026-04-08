"""Registry for shared runtime host projections."""

from __future__ import annotations

from typing import Any, TypeVar

from runtimeV2.runtime import RuntimeV2

T = TypeVar("T")


class SharedRuntimeHostRegistry:
    """Store shared and host-specific runtime host projections."""

    def __init__(self, runtime: RuntimeV2) -> None:
        self._runtime = runtime
        self._capabilities: dict[str, object] = {}

    @property
    def runtime(self) -> RuntimeV2:
        """Return the runtime that backs this host registry."""

        return self._runtime

    def register_capability(self, name: str, capability: object) -> None:
        """Register one shared or host-specific projection capability."""

        self._capabilities[name] = capability

    def capability(self, name: str, capability_type: type[T]) -> T:
        """Return one registered host projection capability."""

        capability = self._capabilities[name]
        if not isinstance(capability, capability_type):
            raise TypeError(
                f"Shared runtime host capability '{name}' is not of type {capability_type.__name__}"
            )
        return capability

    def has_capability(self, name: str) -> bool:
        """Return whether one projection capability is registered."""

        return name in self._capabilities


def create_shared_runtime_host_registry(runtime: RuntimeV2) -> SharedRuntimeHostRegistry:
    """Create an empty shared runtime host registry for one host."""

    return SharedRuntimeHostRegistry(runtime)
