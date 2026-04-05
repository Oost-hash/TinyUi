"""Startup helpers for runtime-owned window state."""

from __future__ import annotations

from typing import Protocol

from runtime_schema import StartupResult, startup_error, startup_ok


class RuntimeUiStartupLike(Protocol):
    """Minimal runtime surface needed to start runtime/ui."""

    def main_window(self) -> object | None: ...
    def window_records(self) -> object: ...


def start_runtime_ui(runtime: RuntimeUiStartupLike) -> StartupResult:
    """Initialize runtime/ui readiness before boot opens host windows."""

    if runtime.main_window() is None:
        return startup_error("No main window available for runtime/ui startup")
    try:
        runtime.window_records()
    except Exception as exc:
        return startup_error(f"runtime/ui startup failed: {exc}")
    return startup_ok()
