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

"""Persistence store exports."""

from runtimeV2.persistence.stores.overlay_index import OverlayIndexRecord, OverlayIndexStore, overlay_store_uuid
from runtimeV2.persistence.stores.overlay_stores import (
    HostPluginStyleStore,
    OverlayLayoutStore,
    OverlayThemeStore,
)
from runtimeV2.persistence.stores.settings import SettingsStore
from runtimeV2.persistence.stores.widget_config import WidgetConfigStore, widget_instance_uuid

__all__ = [
    "HostPluginStyleStore",
    "OverlayIndexRecord",
    "OverlayIndexStore",
    "OverlayLayoutStore",
    "OverlayThemeStore",
    "SettingsStore",
    "WidgetConfigStore",
    "overlay_store_uuid",
    "widget_instance_uuid",
]
