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

"""UI-owned manifest schemas."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class ChromePolicy:
    """Window chrome policy declared by a plugin manifest."""

    show_menu_button: bool = False
    show_title_text: bool = True
    show_caption_buttons: bool = True
    show_tab_bar: bool = False
    show_status_bar: bool = False
    custom_chrome: Path | None = None

    def to_qml_dict(self) -> dict[str, bool]:
        """Return the policy shape expected by current QML."""

        return {
            "showMenuButton": self.show_menu_button,
            "showTitleText": self.show_title_text,
            "showCaptionButtons": self.show_caption_buttons,
            "showTabBar": self.show_tab_bar,
            "showStatusBar": self.show_status_bar,
        }


@dataclass(frozen=True)
class MenuItem:
    """Menu item declaration from a plugin manifest."""

    label: str
    action: str


@dataclass(frozen=True)
class MenuSeparator:
    """Menu separator declaration from a plugin manifest."""


@dataclass(frozen=True)
class StatusbarItemDecl:
    """Statusbar item declaration from a plugin manifest."""

    icon: str = ""
    text: str = ""
    tooltip: str = ""
    action: str = ""
    side: str = "left"


@dataclass(frozen=True)
class AppManifest:
    """Window declaration from a plugin manifest."""

    id: str
    title: str
    surface: Path | None = None
    chrome: ChromePolicy = field(default_factory=ChromePolicy)
    requires: list[str] = field(default_factory=list)
    menu: list[MenuItem | MenuSeparator] = field(default_factory=list)
    statusbar: list[StatusbarItemDecl] = field(default_factory=list)


@dataclass(frozen=True)
class TabDecl:
    """Tab declaration from a plugin manifest."""

    id: str
    label: str
    target: str
    surface: Path
    plugin_id: str


@dataclass(frozen=True)
class UiManifest:
    """UI-specific manifest declarations for host/plugin surfaces."""

    windows: list[AppManifest] = field(default_factory=list)
    tabs: list[TabDecl] = field(default_factory=list)
    plugin_menu: list[MenuItem | MenuSeparator] = field(default_factory=list)
    menu_label: str | None = None
