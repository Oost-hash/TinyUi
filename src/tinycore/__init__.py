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
"""tinycore — generic application engine."""

from .app import App, create_app
from .config.loader import LoaderRegistry, read_json, write_json
from .config.store import ConfigStore
from .editor import ColumnDef, EditorRegistry, EditorSpec, load_editors_toml
from .events.bus import EventBus
from .plugin.protocol import Plugin
from .plugin.registry import PluginRegistry
from .providers.protocol import Provider
from .providers.registry import ProviderRegistry
from .widget import WidgetRegistry, WidgetSpec, load_widgets_toml

__all__ = [
    "App",
    "create_app",
    "ConfigStore",
    "LoaderRegistry",
    "read_json",
    "write_json",
    "ColumnDef",
    "EditorRegistry",
    "EditorSpec",
    "load_editors_toml",
    "EventBus",
    "Plugin",
    "PluginRegistry",
    "Provider",
    "ProviderRegistry",
    "WidgetRegistry",
    "WidgetSpec",
    "load_widgets_toml",
]
