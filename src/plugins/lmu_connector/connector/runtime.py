#  TinyUI
"""Provider-family runtime helpers for the LMU connector."""

from __future__ import annotations

from typing import Protocol


class DemoControllable(Protocol):
    """Optional provider protocol for UI-driven demo mode."""

    def request_demo_mode(self, owner: str) -> None: ...

    def release_demo_mode(self, owner: str) -> None: ...

    def mode(self) -> str: ...

    def active_game(self) -> str: ...

    def active_source(self) -> str: ...

    def supports_demo_mode(self) -> bool: ...
