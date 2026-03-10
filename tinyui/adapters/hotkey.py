#  TinyUI - A mod for TinyPedal
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
#  licensed under GPLv3. TinyPedal is included as a submodule.

"""Hotkey control adapter with state tracking."""

from .lazy import LazyModule


class Hotkey:
    """Manages hotkey state with enable/disable tracking."""

    def __init__(self):
        self._real = LazyModule("tinypedal_repo.tinypedal.hotkey_control", "kctrl")
        self._enabled = False

    def enable(self) -> None:
        """Enable hotkeys (idempotent)."""
        if not self._enabled:
            self._real.enable()
            self._enabled = True

    def disable(self) -> None:
        """Disable hotkeys (idempotent)."""
        if self._enabled:
            self._real.disable()
            self._enabled = False

    def reload(self) -> None:
        """Reload hotkey configuration."""
        self._real.reload()

    @property
    def is_enabled(self) -> bool:
        return self._enabled

    # Delegate all other attributes to real kctrl
    def __getattr__(self, name: str):
        return getattr(self._real, name)
