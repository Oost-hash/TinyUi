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

"""Host shell read capability for runtime V2 host."""

from __future__ import annotations

from runtimeV2.contracts import HostShell
from runtimeV2.plugins.schemas.manifest import PluginManifest


class HostShellRead:
    """Read host shell data."""

    def __init__(self, host_shell: HostShell) -> None:
        self._host_shell = host_shell

    def host_plugin_id(self) -> str:
        """Return the host plugin id."""

        return self._host_shell.host_plugin_id

    def host_manifest(self) -> PluginManifest:
        """Return the host manifest."""

        return self._host_shell.host_manifest

    def host_shell(self) -> HostShell:
        """Return the full host shell read-model."""

        return self._host_shell
