from __future__ import annotations

from collections.abc import Callable
from typing import Protocol


class StateToolbarActionsLike(Protocol):
    def _toggle_state_capture(self) -> None: ...


class RuntimeToolbarActionsLike(Protocol):
    pass


class ConsoleToolbarActionsLike(Protocol):
    def _clear_console(self) -> None: ...


class DevToolsWindowActionsLike(Protocol):
    def close(self) -> bool: ...


def build_devtools_button_actions(window: DevToolsWindowActionsLike) -> dict[str, Callable[[], object]]:
    """Return TinyDevTools-owned footer actions for the native devtools window."""
    return {
        "close": window.close,
    }


def build_state_toolbar_actions(
    *,
    window: StateToolbarActionsLike,
    copy_all: Callable[[], object],
    copy_path: Callable[[], object],
) -> dict[str, Callable[[], object]]:
    """Return TinyDevTools-owned actions for the state toolbar."""
    return {
        "copy_all": copy_all,
        "toggle_capture": window._toggle_state_capture,
        "copy_path": copy_path,
    }


def build_runtime_toolbar_actions(
    *,
    copy_all: Callable[[], object],
) -> dict[str, Callable[[], object]]:
    """Return TinyDevTools-owned actions for the runtime toolbar."""
    return {
        "copy_all": copy_all,
    }


def build_console_toolbar_actions(
    *,
    window: ConsoleToolbarActionsLike,
) -> dict[str, Callable[[], object]]:
    """Return TinyDevTools-owned actions for the console toolbar."""
    return {
        "clear": window._clear_console,
    }
