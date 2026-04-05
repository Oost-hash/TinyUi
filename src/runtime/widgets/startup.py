"""Startup helpers for runtime-owned widget state."""

from __future__ import annotations

from typing import Protocol

from runtime_schema import StartupResult, startup_error, startup_ok


class RuntimeWidgetsStartupLike(Protocol):
    """Minimal runtime surface needed to start runtime/widgets."""

    def active_overlay_widget_records(self) -> object: ...


def start_runtime_widgets(runtime: RuntimeWidgetsStartupLike) -> StartupResult:
    """Initialize runtime/widgets readiness before widget hosting begins."""

    try:
        runtime.active_overlay_widget_records()
    except Exception as exc:
        return startup_error(f"runtime/widgets startup failed: {exc}")
    return startup_ok()
