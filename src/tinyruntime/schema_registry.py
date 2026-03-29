"""Runtime-owned schema registry and change bus."""

from __future__ import annotations

from dataclasses import dataclass, field
import time
from typing import Any, Callable


@dataclass(frozen=True)
class SchemaDescriptor:
    """One registered schema surface owned by a feature or runtime package."""

    schema_id: str
    package: str
    owner: str
    summary: str
    exports: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()


@dataclass(frozen=True)
class SchemaChangeEvent:
    """One published schema change notification."""

    schema_id: str
    producer: str
    change_key: str
    changed_at_ms: int
    payload: Any = None


@dataclass(frozen=True)
class SchemaRegistrationState:
    """Runtime-facing registration snapshot for one schema."""

    descriptor: SchemaDescriptor
    change_count: int = 0
    last_change: SchemaChangeEvent | None = None


SchemaListener = Callable[[SchemaChangeEvent], None]


@dataclass
class _SchemaSlot:
    descriptor: SchemaDescriptor
    listeners: list[SchemaListener] = field(default_factory=list)
    change_count: int = 0
    last_change: SchemaChangeEvent | None = None


class SchemaRegistry:
    """Registry and change bus for runtime-visible schema ownership."""

    def __init__(self) -> None:
        self._schemas: dict[str, _SchemaSlot] = {}
        self._global_listeners: list[SchemaListener] = []

    def register_schema(self, descriptor: SchemaDescriptor) -> None:
        """Register one schema descriptor with the runtime registry."""
        existing = self._schemas.get(descriptor.schema_id)
        if existing is not None:
            if existing.descriptor != descriptor:
                raise ValueError(
                    f"Schema '{descriptor.schema_id}' already registered with different metadata"
                )
            return
        self._schemas[descriptor.schema_id] = _SchemaSlot(descriptor=descriptor)

    def schema_ids(self) -> tuple[str, ...]:
        """Return registered schema ids in stable sort order."""
        return tuple(sorted(self._schemas))

    def schemas(self) -> list[SchemaRegistrationState]:
        """Return registration snapshots for all known schemas."""
        return [
            SchemaRegistrationState(
                descriptor=slot.descriptor,
                change_count=slot.change_count,
                last_change=slot.last_change,
            )
            for _, slot in sorted(self._schemas.items())
        ]

    def schema(self, schema_id: str) -> SchemaRegistrationState | None:
        """Return one registration snapshot by schema id."""
        slot = self._schemas.get(schema_id)
        if slot is None:
            return None
        return SchemaRegistrationState(
            descriptor=slot.descriptor,
            change_count=slot.change_count,
            last_change=slot.last_change,
        )

    def subscribe(
        self,
        listener: SchemaListener,
        *,
        schema_id: str | None = None,
    ) -> Callable[[], None]:
        """Subscribe to schema changes globally or for one schema id."""
        if schema_id is None:
            self._global_listeners.append(listener)

            def _unsubscribe() -> None:
                if listener in self._global_listeners:
                    self._global_listeners.remove(listener)

            return _unsubscribe

        slot = self._schemas.get(schema_id)
        if slot is None:
            raise KeyError(f"Unknown schema '{schema_id}'")
        slot.listeners.append(listener)

        def _unsubscribe() -> None:
            if listener in slot.listeners:
                slot.listeners.remove(listener)

        return _unsubscribe

    def publish_change(
        self,
        schema_id: str,
        *,
        producer: str,
        change_key: str,
        payload: Any = None,
    ) -> SchemaChangeEvent:
        """Publish one schema change event to subscribed listeners."""
        slot = self._schemas.get(schema_id)
        if slot is None:
            raise KeyError(f"Unknown schema '{schema_id}'")
        event = SchemaChangeEvent(
            schema_id=schema_id,
            producer=producer,
            change_key=change_key,
            changed_at_ms=int(time.time() * 1000),
            payload=payload,
        )
        slot.change_count += 1
        slot.last_change = event

        listeners = list(self._global_listeners)
        listeners.extend(slot.listeners)
        for listener in listeners:
            listener(event)
        return event
