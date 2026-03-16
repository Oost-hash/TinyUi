"""Plugin protocol — two-phase lifecycle."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from tinycore.app import App


@runtime_checkable
class Plugin(Protocol):
    """A plugin registers services and has a start/stop lifecycle."""

    @property
    def name(self) -> str: ...

    def register(self, app: App) -> None:
        """Phase 1: register config loaders, providers, event handlers."""
        ...

    def start(self) -> None:
        """Phase 2: called after all plugins are registered."""
        ...

    def stop(self) -> None:
        """Teardown: called in reverse order during shutdown."""
        ...
