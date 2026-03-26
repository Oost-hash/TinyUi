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
"""Consumer plugin protocol — two-phase registration and lifecycle."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from tinycore.plugin.context import PluginContext


@runtime_checkable
class Plugin(Protocol):
    """A consumer plugin registers declarations and has a start/stop lifecycle."""

    @property
    def name(self) -> str: ...

    def register(self, ctx: PluginContext) -> None:
        """Phase 1: register consumer-side declarations such as loaders or editors."""
        ...

    def start(self) -> None:
        """Phase 2: called after all plugins are registered."""
        ...

    def stop(self) -> None:
        """Teardown: called in reverse order during shutdown."""
        ...
