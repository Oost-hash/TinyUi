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

"""UI chrome model projection for runtime V2."""

from __future__ import annotations

from app_schema.ui import MenuItem, MenuSeparator
from runtimeV2.host.capabilities.main_window_read import MainWindowRead
from runtimeV2.plugins.capabilities.active_read import PluginActiveRead
from runtimeV2.plugins.capabilities.ui_manifest_read import PluginUiManifestRead
from runtimeV2.ui.contracts import UIChromeModel, UIMenuItem, UIStatusbarItem, UITabItem


def build_ui_chrome_model(
    *,
    main_window_read: MainWindowRead,
    ui_manifest_read: PluginUiManifestRead,
    active_read: PluginActiveRead,
) -> UIChromeModel:
    """Build the host window chrome model from V2 domain capabilities."""

    main_window = main_window_read.main_window()
    active_plugin_id = active_read.get_active_plugin() or ""
    tabs = [
        UITabItem(
            tab_id=tab.id,
            label=tab.label,
            target=tab.target,
            surface=str(tab.surface),
            plugin_id=plugin_id,
        )
        for plugin_id, plugin_tabs in ui_manifest_read.tabs().items()
        for tab in plugin_tabs
        if tab.target == main_window.id and (plugin_id == "tinyui" or plugin_id == active_plugin_id)
    ]
    return UIChromeModel(
        menu_items=[_menu_item(item) for item in main_window.menu],
        plugin_menu_items=[],
        plugin_menu_label="Plugins",
        statusbar_items=[
            UIStatusbarItem(
                icon=item.icon,
                text=item.text,
                tooltip=item.tooltip,
                action=item.action,
                side=item.side,
            )
            for item in main_window.statusbar
        ],
        tabs=tabs,
        active_plugin_id=active_plugin_id,
        status_active_label=active_plugin_id,
    )


def _menu_item(item: MenuItem | MenuSeparator) -> UIMenuItem:
    if isinstance(item, MenuSeparator):
        return UIMenuItem(separator=True)
    return UIMenuItem(label=item.label, action=item.action)
