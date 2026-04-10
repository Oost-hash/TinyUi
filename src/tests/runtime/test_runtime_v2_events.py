"""Tests for runtime V2 event capabilities."""

from __future__ import annotations

from runtimeV2.events.capabilities.event_registration_write import EventRegistrationWrite
from runtimeV2.contracts import EventBus, EventType
from runtimeV2.events.event_registry import EventRegistry
from runtimeV2.events.capabilities.event_read import EventRead


def test_event_registration_write_registers_event_contract() -> None:
    """Event registration write should expose new contracts through EventRead."""

    bus = EventBus()
    registry = EventRegistry()
    event_read = EventRead(registry)
    event_write = EventRegistrationWrite(registry, bus)

    event_write.register_event("widget_api", EventType.WIDGET_RUNTIME_UPDATED, "Widget sync")

    contract = event_read.event(EventType.WIDGET_RUNTIME_UPDATED)
    assert contract is not None
    assert contract.domain == "widget_api"
    assert contract.description == "Widget sync"


def test_event_registration_write_subscribes_and_closes_listener() -> None:
    """Event registration write should register and close event bus listeners."""

    bus = EventBus()
    registry = EventRegistry()
    event_read = EventRead(registry)
    event_write = EventRegistrationWrite(registry, bus)
    calls: list[EventType] = []

    subscription = event_write.subscribe(
        "shared_runtime_host",
        EventType.WIDGET_RUNTIME_UPDATED,
        lambda event: calls.append(event.type),
        description="Sync widget host",
    )

    assert event_read.listeners_for_event(EventType.WIDGET_RUNTIME_UPDATED)[0].domain == "shared_runtime_host"

    bus.emit_typed(EventType.WIDGET_RUNTIME_UPDATED, data=None, source="widgets")
    subscription.close()
    bus.emit_typed(EventType.WIDGET_RUNTIME_UPDATED, data=None, source="widgets")

    assert calls == [EventType.WIDGET_RUNTIME_UPDATED]
    assert event_read.listeners_for_domain("shared_runtime_host") == []
