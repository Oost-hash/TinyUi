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

"""Chrome model read capability for runtime V2 UI."""

from __future__ import annotations

from runtimeV2.contracts import UIChromeModel, UIMenuItem, UIStatusbarItem, UITabItem


class UIChromeModelRead:
    """Read the UI chrome model."""

    def __init__(self, model: UIChromeModel) -> None:
        self._model = model

    def chrome_model(self) -> UIChromeModel:
        """Return the full chrome model."""

        return self._model

    def tabs(self) -> list[UITabItem]:
        """Return UI tab items."""

        return list(self._model.tabs)

    def menu_items(self) -> list[UIMenuItem]:
        """Return UI menu items."""

        return list(self._model.menu_items)

    def statusbar_items(self) -> list[UIStatusbarItem]:
        """Return UI statusbar items."""

        return list(self._model.statusbar_items)
