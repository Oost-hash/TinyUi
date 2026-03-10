"""Hotkey control adapter with state tracking."""

from .lazy import LazyModule


class Hotkey:
    """Manages hotkey state with enable/disable tracking."""

    def __init__(self):
        self._real = LazyModule("tinypedal_repo.tinypedal.hotkey_control", "kctrl")
        self._enabled = False

    def enable(self) -> None:
        """Enable hotkeys (idempotent)."""
        if not self._enabled:
            self._real.enable()
            self._enabled = True

    def disable(self) -> None:
        """Disable hotkeys (idempotent)."""
        if self._enabled:
            self._real.disable()
            self._enabled = False

    def reload(self) -> None:
        """Reload hotkey configuration."""
        self._real.reload()

    @property
    def is_enabled(self) -> bool:
        return self._enabled

    # Delegate all other attributes to real kctrl
    def __getattr__(self, name: str):
        return getattr(self._real, name)
