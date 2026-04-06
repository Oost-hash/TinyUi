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

"""Base protocol for runtime capabilities."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from runtime.runtime import Runtime


@runtime_checkable
class RuntimeCapability(Protocol):
    """Protocol for capabilities that extend Runtime functionality.

    Each capability encapsulates domain-specific state and behavior,
    keeping Runtime focused on orchestration.
    """

    @property
    def name(self) -> str:
        """Unique name for this capability.

        Used as key in the capability registry.
        """
        ...

    def attach(self, runtime: Runtime) -> None:
        """Called when capability is registered with Runtime.

        Use this to set up event listeners and store runtime reference.
        """
        ...

    def qml_interface(self) -> object | None:
        """Return QML-exposed interface, if any.

        This object will be injected into HostedWindow as a property
        named after the capability.
        """
        ...
