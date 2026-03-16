"""Provider protocol — pull-based data access."""

from __future__ import annotations

from typing import Protocol, TypeVar, runtime_checkable

T = TypeVar("T")


@runtime_checkable
class Provider(Protocol[T]):
    """A provider knows how to produce a value on demand."""

    def get(self) -> T: ...
