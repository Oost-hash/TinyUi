"""Typed startup contract and coordinator for boot-triggered domain startup."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Sequence


@dataclass(frozen=True)
class StartupResult:
    """Minimal result shape for boot-triggered startup steps."""

    ok: bool
    error_message: str = ""


@dataclass(frozen=True)
class StartupStep:
    """One named startup station in the boot pipeline."""

    name: str
    run: Callable[[], StartupResult]


def startup_ok() -> StartupResult:
    """Return a successful startup result."""

    return StartupResult(ok=True)


def startup_error(error_message: str) -> StartupResult:
    """Return a failed startup result with a user-facing reason."""

    return StartupResult(ok=False, error_message=error_message)


def run_startup_pipeline(steps: Sequence[StartupStep]) -> StartupResult:
    """Run startup steps in order and stop at the first failure."""

    for step in steps:
        result = step.run()
        if not result.ok:
            if result.error_message:
                return result
            return startup_error(f"Startup step failed: {step.name}")
    return startup_ok()
