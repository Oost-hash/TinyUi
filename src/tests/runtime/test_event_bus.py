"""Tests for EventBus and event replay functionality."""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from runtime_schema import EventBus, EventType, MenuRegisteredData, TabRegisteredData


class TestEventBus:
    """Test EventBus basic functionality."""
    
    def test_emit_and_receive(self):
        """Test basic emit and receive."""
        bus = EventBus()
        received = []
        
        def handler(event):
            received.append(event)
        
        bus.on(EventType.MENU_REGISTERED, handler)
        bus.emit_typed(EventType.MENU_REGISTERED, MenuRegisteredData(window_id="test"))
        
        assert len(received) == 1
        assert received[0].data.window_id == "test"
    
    def test_history_stores_events(self):
        """Test that events are stored in history."""
        bus = EventBus()
        
        bus.emit_typed(EventType.MENU_REGISTERED, MenuRegisteredData(window_id="test1"))
        bus.emit_typed(EventType.MENU_REGISTERED, MenuRegisteredData(window_id="test2"))
        
        assert len(bus._history) == 2
    
    def test_replay_history(self):
        """Test replay_history=True replays past events."""
        bus = EventBus()
        
        # Emit events before handler subscribes
        bus.emit_typed(EventType.MENU_REGISTERED, MenuRegisteredData(window_id="test1", label="Item 1"))
        bus.emit_typed(EventType.MENU_REGISTERED, MenuRegisteredData(window_id="test2", label="Item 2"))
        bus.emit_typed(EventType.TAB_REGISTERED, TabRegisteredData(window_id="test3"))  # Different type
        
        # Subscribe with replay
        received = []
        def handler(event):
            received.append(event.data.label)
        
        bus.on(EventType.MENU_REGISTERED, handler, replay_history=True)
        
        # Should have received 2 MENU events
        assert len(received) == 2
        assert "Item 1" in received
        assert "Item 2" in received
    
    def test_no_replay_by_default(self):
        """Test that replay is disabled by default."""
        bus = EventBus()
        
        # Emit events before handler subscribes
        bus.emit_typed(EventType.MENU_REGISTERED, MenuRegisteredData(window_id="test1"))
        
        # Subscribe without replay (default)
        received = []
        bus.on(EventType.MENU_REGISTERED, lambda e: received.append(e))
        
        assert len(received) == 0
    
    def test_new_events_received_after_subscribe(self):
        """Test that new events are received after subscription."""
        bus = EventBus()
        received = []
        
        bus.on(EventType.MENU_REGISTERED, lambda e: received.append(e), replay_history=True)
        
        # Emit new event
        bus.emit_typed(EventType.MENU_REGISTERED, MenuRegisteredData(window_id="new"))
        
        assert len(received) == 1


class TestEventData:
    """Test event data classes."""
    
    def test_menu_registered_data(self):
        """Test MenuRegisteredData creation."""
        data = MenuRegisteredData(
            window_id="tinyui.main",
            label="Settings",
            action="open:settings.main",
            source="host"
        )
        
        assert data.window_id == "tinyui.main"
        assert data.label == "Settings"
        assert data.action == "open:settings.main"
        assert data.source == "host"
        assert data.separator is False
    
    def test_menu_separator_data(self):
        """Test MenuRegisteredData for separator."""
        data = MenuRegisteredData(
            window_id="tinyui.main",
            separator=True,
            source="host"
        )
        
        assert data.separator is True
        assert data.label == ""  # Default


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
