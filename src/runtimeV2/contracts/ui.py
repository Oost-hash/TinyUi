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

"""Public UI contracts used outside the ui domain."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from runtimeV2.ui.contracts import UIChromeModel, UIMenuItem, UIStatusbarItem, UITabItem, UIWindowRecord


@runtime_checkable
class WindowRecordsReader(Protocol):
    """Public contract for reading projected UI window records."""

    def all_window_records(self) -> list[UIWindowRecord]:
        """Return all projected UI window records."""
        ...

    def window_record(self, window_id: str) -> UIWindowRecord | None:
        """Return one projected UI window record."""
        ...


@runtime_checkable
class UIChromeModelReader(Protocol):
    """Public contract for reading projected UI chrome data."""

    def chrome_model(self) -> UIChromeModel:
        """Return the full projected UI chrome model."""
        ...

    def tabs(self) -> list[UITabItem]:
        """Return projected UI tab items."""
        ...

    def menu_items(self) -> list[UIMenuItem]:
        """Return projected UI menu items."""
        ...

    def statusbar_items(self) -> list[UIStatusbarItem]:
        """Return projected UI statusbar items."""
        ...


@runtime_checkable
class PanelStateReader(Protocol):
    """Public contract for reading runtime-owned UI panel state."""

    def plugin_panel_visible(self) -> bool:
        """Return whether the runtime plugin panel is visible."""
        ...


@runtime_checkable
class PanelStateWriter(Protocol):
    """Public contract for mutating runtime-owned UI panel state."""

    def set_plugin_panel_visible(self, visible: bool) -> bool:
        """Set whether the runtime plugin panel is visible."""
        ...

    def toggle_plugin_panel(self) -> bool:
        """Toggle runtime-owned plugin panel visibility."""
        ...


@runtime_checkable
class WindowActionsWriter(Protocol):
    """Public contract for runtime-owned UI window actions."""

    def main_window_id(self) -> str:
        """Return the runtime-owned main window id."""
        ...

    def openable_window_ids(self) -> list[str]:
        """Return non-main window ids that the host may open."""
        ...

    def can_open_window(self, window_id: str) -> bool:
        """Return whether one window id is openable through the host."""
        ...

    def request_open_window(self, window_id: str) -> bool:
        """Validate an open-window action request."""
        ...
