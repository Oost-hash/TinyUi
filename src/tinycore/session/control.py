"""Session-owned provider control helpers for UI-facing adapters."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .runtime import SessionRuntime


@dataclass(frozen=True)
class DemoConfig:
    """Provider demo-mode tuning values exposed to UI adapters."""

    minimum: float = 0.0
    maximum: float = 0.0
    speed: float = 0.0


class ProviderControlService:
    """Resolve provider bindings and expose a stable control surface."""

    def __init__(self, session: "SessionRuntime") -> None:
        self._session = session

    def provider_name_for(self, consumer_name: str, capability: str) -> str:
        binding = self._binding(consumer_name, capability)
        return binding.provider_name if binding is not None else ""

    def supports_demo_mode(self, consumer_name: str, capability: str) -> bool:
        provider = self._provider(consumer_name, capability)
        if provider is None:
            return False
        supports_demo = getattr(provider, "supports_demo_mode", None)
        return bool(supports_demo()) if callable(supports_demo) else False

    def request_demo_mode(self, consumer_name: str, capability: str, owner: str) -> bool:
        provider = self._provider(consumer_name, capability)
        if provider is None or not hasattr(provider, "request_demo_mode"):
            return False
        provider.request_demo_mode(owner)
        return True

    def release_demo_mode(self, consumer_name: str, capability: str, owner: str) -> bool:
        provider = self._provider(consumer_name, capability)
        if provider is None or not hasattr(provider, "release_demo_mode"):
            return False
        provider.release_demo_mode(owner)
        return True

    def provider_mode(self, consumer_name: str, capability: str) -> str:
        provider = self._provider(consumer_name, capability)
        if provider is None:
            return "missing"
        mode = getattr(provider, "mode", None)
        return str(mode()) if callable(mode) else "real"

    def active_game(self, consumer_name: str, capability: str) -> str:
        provider = self._provider(consumer_name, capability)
        if provider is None:
            return "none"
        active_game = getattr(provider, "active_game", None)
        return str(active_game()) if callable(active_game) else "unknown"

    def demo_config(self, consumer_name: str, capability: str) -> DemoConfig:
        provider = self._provider(consumer_name, capability)
        if provider is None:
            return DemoConfig()
        return DemoConfig(
            minimum=self._call_float(provider, "demo_min"),
            maximum=self._call_float(provider, "demo_max"),
            speed=self._call_float(provider, "demo_speed"),
        )

    def set_demo_min(self, consumer_name: str, capability: str, value: float) -> bool:
        return self._set_demo_value(consumer_name, capability, "set_demo_min", value)

    def set_demo_max(self, consumer_name: str, capability: str, value: float) -> bool:
        return self._set_demo_value(consumer_name, capability, "set_demo_max", value)

    def set_demo_speed(self, consumer_name: str, capability: str, value: float) -> bool:
        return self._set_demo_value(consumer_name, capability, "set_demo_speed", value)

    def _binding(self, consumer_name: str, capability: str):
        return self._session.bindings_for(consumer_name).get(capability)

    def _provider(self, consumer_name: str, capability: str):
        binding = self._binding(consumer_name, capability)
        return binding.provider if binding is not None else None

    @staticmethod
    def _call_float(provider, name: str) -> float:
        getter = getattr(provider, name, None)
        return float(getter()) if callable(getter) else 0.0

    def _set_demo_value(self, consumer_name: str, capability: str, name: str, value: float) -> bool:
        provider = self._provider(consumer_name, capability)
        setter = getattr(provider, name, None) if provider is not None else None
        if not callable(setter):
            return False
        setter(value)
        return True
