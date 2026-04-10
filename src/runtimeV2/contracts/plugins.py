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

"""Public plugin contracts used outside the plugins domain."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol, runtime_checkable

from runtimeV2.plugins.schemas.lifecycle import PluginState


@runtime_checkable
class PluginDiscovery(Protocol):
    """Public contract for reading discovered plugin ids and roots."""

    def plugin_ids(self) -> list[str]:
        """Return discovered plugin ids."""
        ...

    def plugin_root(self, plugin_id: str) -> Path | None:
        """Return one plugin root."""
        ...

    def import_roots(self) -> set[Path]:
        """Return discovered import roots."""
        ...

    def skipped_packaged_plugins(self) -> set[str]:
        """Return packaged plugins skipped by the read-only slice."""
        ...


@runtime_checkable
class PluginActiveReader(Protocol):
    """Public contract for reading the active plugin."""

    def get_active_plugin(self) -> str | None:
        """Return the active plugin."""
        ...


@runtime_checkable
class PluginActiveWriter(Protocol):
    """Public contract for requesting active plugin changes."""

    def set_active_plugin(self, plugin_id: str) -> bool:
        """Set the active plugin."""
        ...


@runtime_checkable
class PluginStateReader(Protocol):
    """Public contract for reading plugin lifecycle state."""

    def get_plugin_state(self, plugin_id: str) -> PluginState:
        """Return one plugin lifecycle state."""
        ...


@runtime_checkable
class PluginStateWriter(Protocol):
    """Public contract for requesting plugin lifecycle state changes."""

    def enable_plugin(self, plugin_id: str) -> bool:
        """Enable one plugin."""
        ...

    def disable_plugin(self, plugin_id: str) -> bool:
        """Disable one plugin."""
        ...


@runtime_checkable
class PluginIconResolver(Protocol):
    """Public contract for resolving plugin icon file URLs."""

    def get_icon_url(self, plugin_id: str) -> str:
        """Return a safe file URL for one plugin icon."""
        ...
