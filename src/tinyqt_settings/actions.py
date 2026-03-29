from __future__ import annotations

from collections.abc import Callable
from typing import Protocol


class SettingsWindowActionsLike(Protocol):
    def revert_pending_changes(self) -> None: ...
    def apply_pending_changes(self) -> None: ...
    def close(self) -> bool: ...


def build_settings_button_actions(window: SettingsWindowActionsLike) -> dict[str, Callable[[], object]]:
    """Return TinyUI-owned footer actions for the native settings window."""
    return {
        "revert": window.revert_pending_changes,
        "save": window.apply_pending_changes,
        "close": window.close,
    }
