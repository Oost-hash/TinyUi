#  TinyUI
#  Copyright (C) 2026 Oost-hash
#
#  This file is part of TinyUI.
#
#  TinyUI is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  TinyUI is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#  TinyUI builds on TinyPedal by s-victor (https://github.com/s-victor/TinyPedal),
#  licensed under GPLv3.

"""Plugin state machine for lifecycle management."""

from __future__ import annotations

import time
from dataclasses import dataclass

from runtime_schema.plugin import PluginState


@dataclass
class StateTransition:
    """Records a state change."""
    from_state: PluginState
    to_state: PluginState
    timestamp: float
    reason: str = ""


class PluginStateMachine:
    """Manages state transitions for a single plugin."""
    
    # Valid state transitions
    _VALID_TRANSITIONS: dict[PluginState, set[PluginState]] = {
        PluginState.DISABLED: {PluginState.ENABLING},
        PluginState.ENABLING: {PluginState.LOADING, PluginState.DISABLED, PluginState.ERROR},
        PluginState.LOADING: {PluginState.ACTIVE, PluginState.ERROR, PluginState.DISABLED},
        PluginState.ACTIVE: {PluginState.UNLOADING, PluginState.DISABLED},
        PluginState.UNLOADING: {PluginState.DISABLED, PluginState.ERROR},
        PluginState.ERROR: {PluginState.DISABLED, PluginState.ENABLING},
    }
    
    def __init__(self, plugin_id: str) -> None:
        self.plugin_id = plugin_id
        self._state = PluginState.DISABLED
        self._history: list[StateTransition] = []
        self._error_message: str | None = None
    
    @property
    def state(self) -> PluginState:
        """Get current state."""
        return self._state
    
    @property
    def state_name(self) -> str:
        """Get current state name as string."""
        return self._state.name.lower()
    
    @property
    def error_message(self) -> str | None:
        """Get error message if in error state."""
        return self._error_message
    
    @property
    def history(self) -> list[StateTransition]:
        """Get state transition history."""
        return list(self._history)
    
    def _is_valid_transition(self, new_state: PluginState) -> bool:
        """Check if transition to new_state is valid."""
        valid_next = self._VALID_TRANSITIONS.get(self._state, set())
        return new_state in valid_next
    
    def transition(self, new_state: PluginState, reason: str = "") -> bool:
        """Attempt state transition. Returns True on success."""
        if not self._is_valid_transition(new_state):
            return False
        
        transition = StateTransition(
            from_state=self._state,
            to_state=new_state,
            timestamp=time.time(),
            reason=reason
        )
        self._history.append(transition)
        self._state = new_state
        
        # Clear error when leaving error state
        if self._state != PluginState.ERROR:
            self._error_message = None
        
        return True
    
    def set_error(self, message: str) -> None:
        """Transition to error state with message."""
        self._error_message = message
        self.transition(PluginState.ERROR, f"Error: {message}")
    
    def can_transition_to(self, state: PluginState) -> bool:
        """Check if transition to state is allowed."""
        return self._is_valid_transition(state)
    
    def get_time_in_state(self) -> float:
        """Get seconds spent in current state."""
        if not self._history:
            return 0.0
        last_transition = self._history[-1]
        return time.time() - last_transition.timestamp
