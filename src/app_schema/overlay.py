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

"""Overlay-oriented manifest dataclasses."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class WidgetDefaults:
    """Declarative default values for a widget instance, authored by the plugin."""

    enabled: bool = True
    visible: bool = True
    position: tuple[int, int] = (0, 0)


@dataclass(frozen=True)
class OverlayWidgetDecl:
    """Overlay widget declaration from manifest."""

    id: str
    widget: str
    label: str = ""
    bindings: dict[str, str] = field(default_factory=dict)
    defaults: WidgetDefaults = field(default_factory=WidgetDefaults)


@dataclass(frozen=True)
class OverlayManifest:
    """Overlay-specific manifest declarations."""

    connectors: list[str] = field(default_factory=list)
    modules: list[str] = field(default_factory=list)
    widgets: list[OverlayWidgetDecl] = field(default_factory=list)
