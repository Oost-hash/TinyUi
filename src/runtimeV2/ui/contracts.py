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

"""Contracts for runtime V2 UI."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class UIWindowStatus(StrEnum):
    """Observable UI window status."""

    IDLE = "idle"
    READY = "ready"
    ERROR = "error"


@dataclass(frozen=True)
class UIWindowRecord:
    """Projected runtime V2 UI window record."""

    window_id: str
    plugin_id: str
    window_role: str
    status: UIWindowStatus
    visible: bool
    surface: str
    chrome_surface: str = ""
    error_message: str = ""


@dataclass(frozen=True)
class UIRenderStatus:
    """Runtime V2 UI render readiness."""

    render_ready: bool
    render_blocker: str = ""
    main_window_id: str = ""


@dataclass(frozen=True)
class QmlPropertyPlan:
    """Mapping from runtime capability name to QML property name."""

    capability_name: str
    qml_property: str


@dataclass(frozen=True)
class UIMenuItem:
    """UI-facing menu item."""

    label: str = ""
    action: str = ""
    separator: bool = False


@dataclass(frozen=True)
class UIStatusbarItem:
    """UI-facing statusbar item."""

    icon: str = ""
    text: str = ""
    tooltip: str = ""
    action: str = ""
    side: str = "left"


@dataclass(frozen=True)
class UITabItem:
    """UI-facing tab item."""

    tab_id: str
    label: str
    target: str
    surface: str
    plugin_id: str


@dataclass(frozen=True)
class UIChromeModel:
    """UI-facing chrome model for the host window."""

    menu_items: list[UIMenuItem]
    plugin_menu_items: list[UIMenuItem]
    plugin_menu_label: str
    statusbar_items: list[UIStatusbarItem]
    tabs: list[UITabItem]
    active_plugin_id: str
    status_active_label: str


@dataclass(frozen=True)
class UIWindowRecordsChangedData:
    """Data for UI window record updates."""

    window_count: int
