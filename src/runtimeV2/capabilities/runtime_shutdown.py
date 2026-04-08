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

"""Runtime shutdown capability."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from runtimeV2.runtime import RuntimeV2


class RuntimeShutdown:
    """Request and inspect runtime shutdown state."""

    def __init__(self, runtime: RuntimeV2) -> None:
        self._runtime = runtime

    def begin_shutdown(self, reason: str = "app_quit") -> bool:
        """Request runtime shutdown once."""

        return self._runtime.begin_shutdown(reason)

    def shutdown_requested(self) -> bool:
        """Return whether shutdown was already requested."""

        return self._runtime.shutdown_requested()

    def shutdown_reason(self) -> str:
        """Return the current shutdown reason."""

        return self._runtime.shutdown_reason()
