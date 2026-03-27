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
"""ConfigStore — string-keyed config distribution.

A message broker for configuration, not a config manager.
The store has no domain knowledge. It stores named snapshots
and notifies observers on changes.
"""

from __future__ import annotations

from typing import Any, Callable


class ConfigStore:
    """Generic config store with push notifications."""

    def __init__(self):
        self._current: dict[str, Any] = {}
        self._observers: dict[str, list[Callable]] = {}

    def get(self, key: str) -> Any:
        """Get current snapshot for a config key.

        Raises KeyError if the key was never registered.
        """
        return self._current[key]

    def get_or_default(self, key: str, default: Any = None) -> Any:
        """Get current snapshot, or return default if not registered."""
        return self._current.get(key, default)

    def has(self, key: str) -> bool:
        """Check if a config key is registered."""
        return key in self._current

    def update(self, key: str, value: Any) -> None:
        """Publish a new value. Notifies all observers of this key."""
        self._current[key] = value
        for callback in self._observers.get(key, []):
            callback(value)

    def observe(self, key: str, callback: Callable[[Any], None]) -> Callable:
        """Subscribe to changes for a config key.

        Returns an unsubscribe function.
        """
        self._observers.setdefault(key, []).append(callback)

        def unsubscribe():
            self._observers[key].remove(callback)

        return unsubscribe

    @property
    def registered_keys(self) -> set[str]:
        """All currently registered config keys."""
        return set(self._current.keys())
