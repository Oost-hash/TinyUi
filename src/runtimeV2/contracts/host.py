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

"""Public host contracts used outside the host domain."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from runtimeV2.host.contracts import HostAppIdentity, HostShell
from runtimeV2.plugins.schemas.manifest import PluginManifest
from runtimeV2.ui.schemas.manifest import AppManifest


@runtime_checkable
class MainWindowReader(Protocol):
    """Public contract for reading the host main window."""

    def main_window(self) -> AppManifest:
        """Return the host main window."""
        ...

    def main_window_id(self) -> str:
        """Return the host main window id."""
        ...


@runtime_checkable
class AppIdentityReader(Protocol):
    """Public contract for reading app identity derived from the host plugin."""

    def identity(self) -> HostAppIdentity:
        """Return the full app identity."""
        ...

    def app_id(self) -> str:
        """Return the app id."""
        ...

    def app_version(self) -> str:
        """Return the app version."""
        ...

    def app_title(self) -> str:
        """Return the app title."""
        ...


@runtime_checkable
class HostShellReader(Protocol):
    """Public contract for reading host shell data."""

    def host_plugin_id(self) -> str:
        """Return the host plugin id."""
        ...

    def host_manifest(self) -> PluginManifest:
        """Return the host manifest."""
        ...

    def host_shell(self) -> HostShell:
        """Return the full host shell read-model."""
        ...
