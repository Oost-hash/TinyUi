"""Tests for Runtime boot sequence - no Qt dependencies."""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from runtime_schema import EventBus, EventType, BootInitData, MenuRegisteredData


class MockRuntime:
    """Mock Runtime that doesn't depend on Qt/AppPaths."""
    
    def __init__(self, event_bus):
        self.events = event_bus
        self._plugins = {}
        self._menu_registered = False
        self.events.on(EventType.BOOT_INIT, self._on_boot_init)
    
    def _on_boot_init(self, event):
        """Handle boot init."""
        data = event.data
        # Simulate boot sequence
        self._register_menus()
    
    def _register_menus(self):
        """Simulate menu registration."""
        # Emit some menu events
        self.events.emit_typed(EventType.MENU_REGISTERED, MenuRegisteredData(
            window_id="tinyui.main",
            label="Settings",
            action="open:settings.main",
            source="host"
        ))
        self.events.emit_typed(EventType.MENU_REGISTERED, MenuRegisteredData(
            window_id="tinyui.main",
            label="Close",
            action="close",
            source="host"
        ))
        self._menu_registered = True


class TestRuntimeBoot:
    """Test Runtime boot sequence."""
    
    def test_boot_emits_events(self):
        """Test that boot emits MENU_REGISTERED events."""
        bus = EventBus()
        runtime = MockRuntime(bus)
        
        # Track menu events
        menu_events = []
        bus.on(EventType.MENU_REGISTERED, lambda e: menu_events.append(e.data.label))
        
        # Emit boot init
        bus.emit_typed(EventType.BOOT_INIT, BootInitData(
            config_dir="/tmp/config",
            plugins_dir="/tmp/plugins",
            data_dir="/tmp/data"
        ))
        
        # Should have received menu events
        assert len(menu_events) == 2
        assert "Settings" in menu_events
        assert "Close" in menu_events
    
    def test_late_subscriber_gets_replay(self):
        """Test that late subscriber can replay boot events."""
        bus = EventBus()
        runtime = MockRuntime(bus)
        
        # Boot first
        bus.emit_typed(EventType.BOOT_INIT, BootInitData(
            config_dir="/tmp/config",
            plugins_dir="/tmp/plugins",
            data_dir="/tmp/data"
        ))
        
        # Now subscribe late with replay
        late_events = []
        bus.on(EventType.MENU_REGISTERED, lambda e: late_events.append(e.data.label), replay_history=True)
        
        # Should have received the events
        assert len(late_events) == 2
        assert "Settings" in late_events


class TestEventOrdering:
    """Test event ordering during boot."""
    
    def test_events_in_order(self):
        """Test that events are stored and replayed in order."""
        bus = EventBus()
        
        # Emit events in specific order
        for i in range(5):
            bus.emit_typed(EventType.MENU_REGISTERED, MenuRegisteredData(
                window_id="test",
                label=f"Item {i}",
                action=f"action{i}"
            ))
        
        # Subscribe with replay
        received = []
        bus.on(EventType.MENU_REGISTERED, lambda e: received.append(e.data.label), replay_history=True)
        
        # Check order is preserved
        assert [f"Item {i}" for i in range(5)] == received


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
